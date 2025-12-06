import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, MapPin, Save, Loader2, CreditCard, Image as ImageIcon, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getUserProfile, updateUserProfile, UserProfile, UpdateProfileData } from '../api/auth';

const ProfilePage: React.FC = () => {
  const { user, token, updateUser } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
  });
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      if (!user || !token) {
        setError('Please sign in to view your profile');
        setLoading(false);
        return;
      }

      try {
        const userProfile = await getUserProfile(user.user_id, token);
        setProfile(userProfile);
        setFormData({
          first_name: userProfile.first_name || '',
          last_name: userProfile.last_name || '',
          email: userProfile.email || '',
          phone_number: userProfile.phone_number || '',
          address: userProfile.address || '',
          city: userProfile.city || '',
          state: userProfile.state || '',
          zip_code: userProfile.zip_code || '',
        });
        // Set image preview if profile has image
        if (userProfile.profile_image_url) {
          setImagePreview(userProfile.profile_image_url);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [user, token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size must be less than 5MB');
        return;
      }
      setProfileImage(file);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setError('');
    }
  };

  const removeImage = () => {
    setProfileImage(null);
    // Keep existing image preview if available
    if (profile?.profile_image_url) {
      setImagePreview(profile.profile_image_url);
    } else {
      setImagePreview(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !token) {
      setError('Please sign in to update your profile');
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const updateData: UpdateProfileData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        phone_number: formData.phone_number || undefined,
        address: formData.address || undefined,
        city: formData.city || undefined,
        state: formData.state || undefined,
        zip_code: formData.zip_code || undefined,
      };

      const updatedProfile = await updateUserProfile(user.user_id, updateData, token, profileImage || undefined);
      setProfile(updatedProfile);
      
      // Update AuthContext with new user data
      updateUser({
        user_id: updatedProfile.user_id,
        first_name: updatedProfile.first_name,
        last_name: updatedProfile.last_name,
        email: updatedProfile.email,
        phone_number: updatedProfile.phone_number,
        is_active: updatedProfile.is_active,
        created_at: updatedProfile.created_at,
        updated_at: updatedProfile.updated_at,
      });

      setSuccess('Profile updated successfully!');
      setIsEditing(false);
      // Reset image file after successful update
      setProfileImage(null);
      // Update image preview with new URL if available
      if (updatedProfile.profile_image_url) {
        setImagePreview(updatedProfile.profile_image_url);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 flex items-center justify-center">
        <Loader2 size={32} className="animate-spin text-slate-600" />
      </div>
    );
  }

  if (!user || !token) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          Please sign in to view your profile.
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">My Profile</h1>
          <p className="text-slate-600">Manage your account information and preferences</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {success}
          </div>
        )}

        <div className="card p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-slate-900">Personal Information</h2>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="btn-secondary flex items-center space-x-2"
              >
                <User size={18} />
                <span>Edit Profile</span>
              </button>
            )}
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Profile Image Upload */}
            {isEditing && (
              <div>
                <label htmlFor="profileImage" className="block text-sm font-medium text-slate-700 mb-1.5">
                  Profile Image
                </label>
                <div className="flex items-center space-x-4">
                  {imagePreview ? (
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Profile preview"
                        className="w-24 h-24 rounded-full object-cover border-2 border-slate-300"
                      />
                      <button
                        type="button"
                        onClick={removeImage}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : profile?.profile_image_url ? (
                    <img
                      src={profile.profile_image_url}
                      alt="Current profile"
                      className="w-24 h-24 rounded-full object-cover border-2 border-slate-300"
                    />
                  ) : (
                    <div className="w-24 h-24 rounded-full bg-slate-100 border-2 border-dashed border-slate-300 flex items-center justify-center">
                      <ImageIcon className="h-10 w-10 text-slate-400" />
                    </div>
                  )}
                  <div className="flex-1">
                    <input
                      id="profileImage"
                      name="profileImage"
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="block w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
                    />
                    <p className="mt-1 text-xs text-slate-500">JPG, PNG, GIF or WEBP (max 5MB)</p>
                  </div>
                </div>
              </div>
            )}
            {!isEditing && profile?.profile_image_url && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Profile Image
                </label>
                <img
                  src={profile.profile_image_url}
                  alt="Profile"
                  className="w-24 h-24 rounded-full object-cover border-2 border-slate-300"
                />
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* User ID (Read-only) */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  User ID (SSN)
                </label>
                <div className="flex items-center border border-slate-300 rounded-lg px-4 py-2.5 bg-slate-50">
                  <CreditCard className="h-5 w-5 text-slate-400 mr-3" />
                  <span className="text-slate-900">{profile?.user_id || user.user_id}</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">User ID cannot be changed</p>
              </div>

              {/* Email (Read-only) */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Email Address
                </label>
                <div className="flex items-center border border-slate-300 rounded-lg px-4 py-2.5 bg-slate-50">
                  <Mail className="h-5 w-5 text-slate-400 mr-3" />
                  <span className="text-slate-900">{profile?.email || user.email}</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">Email cannot be changed</p>
              </div>

              {/* First Name */}
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-slate-700 mb-1.5">
                  First Name
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed"
                />
              </div>

              {/* Last Name */}
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-slate-700 mb-1.5">
                  Last Name
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed"
                />
              </div>

              {/* Phone Number */}
              <div>
                <label htmlFor="phone_number" className="block text-sm font-medium text-slate-700 mb-1.5">
                  Phone Number
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Phone className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    id="phone_number"
                    name="phone_number"
                    type="tel"
                    value={formData.phone_number}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="block w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed"
                    placeholder="555-123-4567"
                  />
                </div>
              </div>

              {/* Address */}
              <div>
                <label htmlFor="address" className="block text-sm font-medium text-slate-700 mb-1.5">
                  Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MapPin className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    id="address"
                    name="address"
                    type="text"
                    value={formData.address}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="block w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed"
                    placeholder="123 Main Street"
                  />
                </div>
              </div>

              {/* City */}
              <div>
                <label htmlFor="city" className="block text-sm font-medium text-slate-700 mb-1.5">
                  City
                </label>
                <input
                  id="city"
                  name="city"
                  type="text"
                  value={formData.city}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed"
                  placeholder="San Jose"
                />
              </div>

              {/* State */}
              <div>
                <label htmlFor="state" className="block text-sm font-medium text-slate-700 mb-1.5">
                  State
                </label>
                <input
                  id="state"
                  name="state"
                  type="text"
                  maxLength={2}
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value.toUpperCase() })}
                  disabled={!isEditing}
                  className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed uppercase"
                  placeholder="CA"
                />
                <p className="mt-1 text-xs text-slate-500">2-letter code</p>
              </div>

              {/* ZIP Code */}
              <div>
                <label htmlFor="zip_code" className="block text-sm font-medium text-slate-700 mb-1.5">
                  ZIP Code
                </label>
                <input
                  id="zip_code"
                  name="zip_code"
                  type="text"
                  value={formData.zip_code}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="block w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-700 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed"
                  placeholder="95123"
                />
                <p className="mt-1 text-xs text-slate-500">Format: XXXXX or XXXXX-XXXX</p>
              </div>
            </div>

            {/* Account Info (Read-only) */}
            <div className="pt-6 border-t border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Account Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-600">Account Status:</span>
                  <span className={`ml-2 font-semibold ${profile?.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {profile?.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-600">Member Since:</span>
                  <span className="ml-2 font-semibold text-slate-900">
                    {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
                {profile?.credit_card_last_four && (
                  <div>
                    <span className="text-slate-600">Payment Method:</span>
                    <span className="ml-2 font-semibold text-slate-900">
                      •••• {profile.credit_card_last_four}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex justify-end space-x-4 pt-6 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setProfileImage(null);
                    // Reset form data to original profile
                    if (profile) {
                      setFormData({
                        first_name: profile.first_name || '',
                        last_name: profile.last_name || '',
                        email: profile.email || '',
                        phone_number: profile.phone_number || '',
                        address: profile.address || '',
                        city: profile.city || '',
                        state: profile.state || '',
                        zip_code: profile.zip_code || '',
                      });
                      // Reset image preview to original
                      if (profile.profile_image_url) {
                        setImagePreview(profile.profile_image_url);
                      } else {
                        setImagePreview(null);
                      }
                    }
                    setError('');
                    setSuccess('');
                  }}
                  className="btn-secondary px-6 py-2.5"
                  disabled={saving}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="btn-primary px-6 py-2.5 flex items-center space-x-2"
                >
                  {saving ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Save size={18} />
                      <span>Save Changes</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
