import React, { useCallback, useEffect, useState, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { Camera, Trash2, Save, Loader2, AlertTriangle, Settings, FileText, ChevronRight } from 'lucide-react';

interface UserProfile {
  id: number;
  email: string;
  username: string;
  pictureURL: string | null;
  userDescriptionURL: string | null;
}

/** GCS v4 signed URLs must not get extra query params — that invalidates the signature. */
function isGcsSignedUrl(url: string): boolean {
  return url.includes('X-Goog-Signature') || url.includes('X-Goog-Algorithm=');
}

function pictureUrlForAvatar(baseUrl: string, version: number): string {
  if (isGcsSignedUrl(baseUrl)) return baseUrl;
  return `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}v=${version}`;
}

export default function Dashboard() {
  const { userEmail, logout, login } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [description, setDescription] = useState('');
  const [savingDesc, setSavingDesc] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);
  const [savingAccount, setSavingAccount] = useState(false);
  const [accountUsername, setAccountUsername] = useState('');
  const [accountEmail, setAccountEmail] = useState('');
  const [activeTab, setActiveTab] = useState<'profile' | 'settings'>('profile');
  const [avatarVersion, setAvatarVersion] = useState(0);
  const avatarLoadErrorShown = useRef(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchProfile = useCallback(async () => {
    if (!userEmail) {
      return;
    }
    try {
      const res = await api.get(`/user/${encodeURIComponent(userEmail)}`, {
        params: { _: Date.now() },
      });
      setProfile(res.data);
      if (res.data.userDescriptionURL) {
        try {
          const descRes = await fetch(res.data.userDescriptionURL);
          const descData = await descRes.json();
          setDescription(descData.description || '');
        } catch (e) {
          console.error('Could not fetch description JSON', e);
        }
      }
    } catch {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, [userEmail]);

  useEffect(() => {
    if (!userEmail) {
      return;
    }
    setLoading(true);
    void fetchProfile();
  }, [userEmail, fetchProfile]);

  useEffect(() => {
    if (profile) {
      setAccountUsername(profile.username);
      setAccountEmail(profile.email);
    }
  }, [profile]);

  useEffect(() => {
    avatarLoadErrorShown.current = false;
  }, [profile?.pictureURL]);

  const pictureSrc =
    profile?.pictureURL != null && profile.pictureURL !== ''
      ? pictureUrlForAvatar(profile.pictureURL, avatarVersion)
      : undefined;

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploadingPhoto(true);
    try {
      const res = await api.post<{
        success?: boolean;
        url?: string;
      }>(`/user/${encodeURIComponent(userEmail!)}/profile-photo`, formData);
      const newUrl = res.data?.url;
      if (newUrl) {
        setProfile((prev) => (prev ? { ...prev, pictureURL: newUrl } : prev));
      }
      toast.success('Profile photo updated');
      await fetchProfile();
      setAvatarVersion((n) => n + 1);
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { message?: string }; status?: number } };
      const msg =
        ax.response?.data?.message ||
        (ax.response?.status === 503
          ? 'Cloud storage unavailable — check GCP credentials in .env and credentials/.'
          : 'Failed to upload photo');
      toast.error(msg);
    } finally {
      setUploadingPhoto(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDeletePhoto = async () => {
    try {
      await api.delete(`/user/${encodeURIComponent(userEmail!)}/profile-photo`);
      toast.success('Profile photo removed');
      setProfile((prev) => (prev ? { ...prev, pictureURL: null } : prev));
      await fetchProfile();
      setAvatarVersion((n) => n + 1);
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { message?: string } } };
      toast.error(ax.response?.data?.message || 'Failed to remove photo');
    }
  };

  const handleSaveDescription = async () => {
    setSavingDesc(true);
    try {
      await api.post(`/user/${encodeURIComponent(userEmail!)}/description`, { description });
      toast.success('Description updated');
      fetchProfile();
    } catch {
      toast.error('Failed to update description');
    } finally {
      setSavingDesc(false);
    }
  };

  const handleDeleteDescription = async () => {
    try {
      await api.delete(`/user/${encodeURIComponent(userEmail!)}/description`);
      setDescription('');
      toast.success('Description removed');
      fetchProfile();
    } catch {
      toast.error('Failed to remove description');
    }
  };

  const handleSaveAccount = async () => {
    if (!userEmail) return;
    const u = accountUsername.trim();
    const e = accountEmail.trim();
    if (!u || !e) {
      toast.error('Username and email are required.');
      return;
    }
    setSavingAccount(true);
    try {
      const res = await api.patch(
        `/user/${encodeURIComponent(userEmail)}`,
        { username: u, email: e }
      );
      if (res.data.success) {
        toast.success('Account updated');
        if (e !== userEmail) {
          login(e);
        }
        if (res.data.user) {
          setProfile(res.data.user);
        } else {
          fetchProfile();
        }
      }
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { message?: string } } };
      toast.error(ax.response?.data?.message || 'Failed to update account');
    } finally {
      setSavingAccount(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }
    setDeletingAccount(true);
    try {
      await api.delete(`/user/${encodeURIComponent(userEmail!)}`);
      toast.success('Account deleted successfully');
      logout();
    } catch {
      toast.error('Failed to delete account');
      setDeletingAccount(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="flex-1 w-full max-w-6xl mx-auto p-4 md:p-8">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 space-y-6">
          <div className="panel p-6 text-center relative overflow-hidden group">
            <div className="relative mx-auto w-32 h-32 mb-6">
              <div className="relative z-10 w-full h-full">
                <Avatar
                  key={`${profile?.pictureURL ?? 'none'}-${avatarVersion}`}
                  className="w-full h-full border-2 border-zinc-700 bg-zinc-900"
                >
                  <AvatarImage
                    src={pictureSrc}
                    alt={profile?.username}
                    className="object-cover"
                    onError={() => {
                      if (avatarLoadErrorShown.current) return;
                      avatarLoadErrorShown.current = true;
                      toast.error(
                        'Photo URL saved but the image did not load. In GCP Console: open the bucket → Permissions → grant public read to objects, or use signed URLs.'
                      );
                    }}
                  />
                  <AvatarFallback className="text-3xl font-medium text-zinc-300">
                    {profile?.username?.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <label
                  htmlFor="photo-upload"
                  className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity rounded-full cursor-pointer"
                >
                  {uploadingPhoto ? <Loader2 className="h-6 w-6 animate-spin" /> : <Camera className="h-6 w-6" />}
                  <span className="text-xs mt-1 font-medium">Upload</span>
                </label>
                <input
                  id="photo-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  ref={fileInputRef}
                  onChange={handlePhotoUpload}
                  disabled={uploadingPhoto}
                />
              </div>
            </div>

            <h2 className="text-xl font-bold text-white mb-1">{profile?.username}</h2>
            <p className="text-zinc-500 text-sm mb-6">{profile?.email}</p>

            {profile?.pictureURL && (
              <Button
                variant="ghost"
                size="sm"
                className="w-full text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg"
                onClick={handleDeletePhoto}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Remove photo
              </Button>
            )}
          </div>

          <div className="panel p-2 flex flex-col gap-1">
            <button
              type="button"
              onClick={() => setActiveTab('profile')}
              className={`flex items-center justify-between w-full p-4 rounded-xl text-left transition-colors ${
                activeTab === 'profile' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
              }`}
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5" />
                <span className="font-medium">Profile</span>
              </div>
              {activeTab === 'profile' && <ChevronRight className="w-4 h-4" />}
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('settings')}
              className={`flex items-center justify-between w-full p-4 rounded-xl text-left transition-colors ${
                activeTab === 'settings' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
              }`}
            >
              <div className="flex items-center gap-3">
                <Settings className="w-5 h-5" />
                <span className="font-medium">Settings</span>
              </div>
              {activeTab === 'settings' && <ChevronRight className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div className="lg:col-span-8">
          <div className="panel rounded-2xl p-8 md:p-10 min-h-[520px]">
            {activeTab === 'profile' ? (
              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">About you</h3>
                  <p className="text-zinc-500 text-sm">
                    Description is stored as JSON in Google Cloud Storage; the app loads it when you open the dashboard.
                  </p>
                </div>

                <div className="space-y-4">
                  <textarea
                    id="description"
                    rows={8}
                    className="flex w-full rounded-lg border border-zinc-700 bg-zinc-950 px-4 py-3 text-sm text-white placeholder:text-zinc-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600/50 resize-none"
                    placeholder="Short bio or notes for the demo…"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />

                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <Button
                      onClick={handleSaveDescription}
                      disabled={savingDesc}
                      className="h-10 px-6 rounded-lg bg-white text-black hover:bg-zinc-200"
                    >
                      {savingDesc ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                      Save
                    </Button>

                    {profile?.userDescriptionURL && (
                      <Button
                        variant="ghost"
                        className="h-10 px-4 rounded-lg text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        onClick={handleDeleteDescription}
                      >
                        Clear description
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-10">
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Account</h3>
                  <p className="text-zinc-500 text-sm">
                    Update your username and email. User ID is fixed by the database.
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="grid gap-2">
                    <Label className="text-zinc-500 text-xs">User ID</Label>
                    <Input
                      value={profile?.id ?? ''}
                      readOnly
                      className="bg-zinc-950 border-zinc-800 text-zinc-500 h-10 rounded-lg"
                      aria-readonly
                    />
                    <p className="text-xs text-zinc-600">Primary key — not editable.</p>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="settings-username" className="text-zinc-500 text-xs">
                      Username
                    </Label>
                    <Input
                      id="settings-username"
                      value={accountUsername}
                      onChange={(ev) => setAccountUsername(ev.target.value)}
                      className="bg-zinc-950 border-zinc-700 text-zinc-100 h-10 rounded-lg"
                      autoComplete="username"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="settings-email" className="text-zinc-500 text-xs">
                      Email
                    </Label>
                    <Input
                      id="settings-email"
                      type="email"
                      value={accountEmail}
                      onChange={(ev) => setAccountEmail(ev.target.value)}
                      className="bg-zinc-950 border-zinc-700 text-zinc-100 h-10 rounded-lg"
                      autoComplete="email"
                    />
                  </div>
                  <Button
                    type="button"
                    onClick={handleSaveAccount}
                    disabled={savingAccount}
                    className="h-10 px-6 rounded-lg bg-white text-black hover:bg-zinc-200"
                  >
                    {savingAccount ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save changes
                      </>
                    )}
                  </Button>
                </div>

                <Separator className="bg-zinc-800" />

                <div className="space-y-4 rounded-xl border border-red-900/50 bg-red-950/20 p-6">
                  <div className="flex items-center gap-3 text-red-400">
                    <AlertTriangle className="h-5 w-5 shrink-0" />
                    <h3 className="text-lg font-semibold">Danger zone</h3>
                  </div>
                  <p className="text-zinc-400 text-sm leading-relaxed">
                    Deletes your user row and associated objects in cloud storage. Cannot be undone.
                  </p>
                  <Button
                    variant="destructive"
                    className="h-10 px-4 rounded-lg bg-red-600 hover:bg-red-700 text-white"
                    onClick={handleDeleteAccount}
                    disabled={deletingAccount}
                  >
                    {deletingAccount ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Trash2 className="w-4 h-4 mr-2" />}
                    Delete account
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
