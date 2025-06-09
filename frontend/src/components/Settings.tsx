import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Download, 
  Upload,
  Moon,
  Sun,
  Volume2,
  VolumeX,
  Smartphone,
  Mail,
  MessageSquare
} from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { WolfyAvatar } from './WolfyAvatar';

interface SettingsState {
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
    sound: boolean;
    portfolio: boolean;
    news: boolean;
    alerts: boolean;
  };
  appearance: {
    darkMode: boolean;
    animations: boolean;
    wolfyVisible: boolean;
  };
  privacy: {
    analytics: boolean;
    dataSharing: boolean;
    autoBackup: boolean;
  };
  profile: {
    name: string;
    email: string;
    riskTolerance: number;
  };
}

export function Settings() {
  const [settings, setSettings] = useState<SettingsState>({
    notifications: {
      email: true,
      push: true,
      sms: false,
      sound: true,
      portfolio: true,
      news: true,
      alerts: true,
    },
    appearance: {
      darkMode: true,
      animations: true,
      wolfyVisible: true,
    },
    privacy: {
      analytics: true,
      dataSharing: false,
      autoBackup: true,
    },
    profile: {
      name: 'John Doe',
      email: 'john.doe@example.com',
      riskTolerance: 6,
    }
  });

  const updateSetting = (category: keyof SettingsState, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const SettingItem = ({ 
    icon, 
    title, 
    description, 
    children 
  }: { 
    icon: React.ReactNode;
    title: string;
    description: string;
    children: React.ReactNode;
  }) => (
    <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg border border-slate-700">
      <div className="flex items-center gap-3">
        <div className="text-teal-400">{icon}</div>
        <div>
          <p className="font-medium text-slate-100">{title}</p>
          <p className="text-sm text-slate-400">{description}</p>
        </div>
      </div>
      {children}
    </div>
  );

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-slate-950 to-slate-900 min-h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Settings</h1>
          <p className="text-slate-400">Customize your Wolfy experience</p>
        </div>
        <div className="flex items-center gap-3">
          <WolfyAvatar size="md" isActive={settings.appearance.wolfyVisible} />
          <Button variant="outline" className="border-slate-700 bg-slate-800/50">
            <Download size={16} className="mr-2" />
            Export Settings
          </Button>
        </div>
      </div>

      {/* Settings Content */}
      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="bg-slate-800/50 border border-slate-700">
          <TabsTrigger value="profile" className="data-[state=active]:bg-teal-500/20">
            <User size={16} className="mr-2" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="notifications" className="data-[state=active]:bg-teal-500/20">
            <Bell size={16} className="mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="appearance" className="data-[state=active]:bg-teal-500/20">
            <Palette size={16} className="mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="privacy" className="data-[state=active]:bg-teal-500/20">
            <Shield size={16} className="mr-2" />
            Privacy
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Profile Information</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-slate-300">Full Name</Label>
                  <Input
                    id="name"
                    value={settings.profile.name}
                    onChange={(e) => updateSetting('profile', 'name', e.target.value)}
                    className="bg-slate-900/50 border-slate-700 text-slate-200"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-slate-300">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={settings.profile.email}
                    onChange={(e) => updateSetting('profile', 'email', e.target.value)}
                    className="bg-slate-900/50 border-slate-700 text-slate-200"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label className="text-slate-300">Risk Tolerance: {settings.profile.riskTolerance}/10</Label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={settings.profile.riskTolerance}
                  onChange={(e) => updateSetting('profile', 'riskTolerance', parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Conservative</span>
                  <span>Aggressive</span>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Notification Preferences</h3>
            <div className="space-y-4">
              <SettingItem
                icon={<Mail size={20} />}
                title="Email Notifications"
                description="Receive updates via email"
              >
                <Switch
                  checked={settings.notifications.email}
                  onCheckedChange={(checked) => updateSetting('notifications', 'email', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={<Smartphone size={20} />}
                title="Push Notifications"
                description="Get real-time alerts on your device"
              >
                <Switch
                  checked={settings.notifications.push}
                  onCheckedChange={(checked) => updateSetting('notifications', 'push', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={<MessageSquare size={20} />}
                title="SMS Notifications"
                description="Critical alerts via text message"
              >
                <Switch
                  checked={settings.notifications.sms}
                  onCheckedChange={(checked) => updateSetting('notifications', 'sms', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={settings.notifications.sound ? <Volume2 size={20} /> : <VolumeX size={20} />}
                title="Sound Alerts"
                description="Play sounds for notifications"
              >
                <Switch
                  checked={settings.notifications.sound}
                  onCheckedChange={(checked) => updateSetting('notifications', 'sound', checked)}
                />
              </SettingItem>

              <Separator className="bg-slate-700" />

              <h4 className="font-medium text-slate-200">Alert Types</h4>

              <SettingItem
                icon={<Shield size={20} />}
                title="Portfolio Alerts"
                description="Risk changes and rebalancing suggestions"
              >
                <Switch
                  checked={settings.notifications.portfolio}
                  onCheckedChange={(checked) => updateSetting('notifications', 'portfolio', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={<Bell size={20} />}
                title="Market News"
                description="Important market updates and analysis"
              >
                <Switch
                  checked={settings.notifications.news}
                  onCheckedChange={(checked) => updateSetting('notifications', 'news', checked)}
                />
              </SettingItem>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="appearance" className="space-y-6">
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Appearance & Interface</h3>
            <div className="space-y-4">
              <SettingItem
                icon={settings.appearance.darkMode ? <Moon size={20} /> : <Sun size={20} />}
                title="Dark Mode"
                description="Use dark theme (recommended)"
              >
                <Switch
                  checked={settings.appearance.darkMode}
                  onCheckedChange={(checked) => updateSetting('appearance', 'darkMode', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={<Palette size={20} />}
                title="Animations"
                description="Enable smooth transitions and effects"
              >
                <Switch
                  checked={settings.appearance.animations}
                  onCheckedChange={(checked) => updateSetting('appearance', 'animations', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={<WolfyAvatar size="sm" />}
                title="Show Wolfy"
                description="Display the Wolfy mascot throughout the app"
              >
                <Switch
                  checked={settings.appearance.wolfyVisible}
                  onCheckedChange={(checked) => updateSetting('appearance', 'wolfyVisible', checked)}
                />
              </SettingItem>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="privacy" className="space-y-6">
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Privacy & Security</h3>
            <div className="space-y-4">
              <SettingItem
                icon={<Shield size={20} />}
                title="Analytics"
                description="Help improve Wolfy by sharing usage data"
              >
                <Switch
                  checked={settings.privacy.analytics}
                  onCheckedChange={(checked) => updateSetting('privacy', 'analytics', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={<Upload size={20} />}
                title="Data Sharing"
                description="Share anonymous portfolio insights with research partners"
              >
                <Switch
                  checked={settings.privacy.dataSharing}
                  onCheckedChange={(checked) => updateSetting('privacy', 'dataSharing', checked)}
                />
              </SettingItem>

              <SettingItem
                icon={<Download size={20} />}
                title="Auto Backup"
                description="Automatically backup your portfolio data"
              >
                <Switch
                  checked={settings.privacy.autoBackup}
                  onCheckedChange={(checked) => updateSetting('privacy', 'autoBackup', checked)}
                />
              </SettingItem>
            </div>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Data Management</h3>
            <div className="flex gap-3">
              <Button variant="outline" className="border-slate-700 bg-slate-800/50">
                <Download size={16} className="mr-2" />
                Export Data
              </Button>
              <Button variant="outline" className="border-red-700 bg-red-800/20 text-red-400 hover:bg-red-800/30">
                <Upload size={16} className="mr-2" />
                Delete Account
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}