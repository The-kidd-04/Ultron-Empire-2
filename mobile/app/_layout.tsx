import React from 'react';
import { Tabs } from 'expo-router';
import { Platform, StyleSheet, View, Text } from 'react-native';

const TEAL = '#003235';
const EMERALD = '#008C6F';
const MINT = '#63D2B7';
const INACTIVE = '#8E9BAE';

function TabIcon({ label, focused }: { label: string; focused: boolean }) {
  const icons: Record<string, string> = {
    Home: '\uD83C\uDFE0',
    Chat: '\uD83D\uDCAC',
    Clients: '\uD83D\uDC65',
    Market: '\uD83D\uDCC8',
    Alerts: '\uD83D\uDD14',
  };
  return (
    <View style={tabStyles.iconWrap}>
      <Text style={[tabStyles.icon, focused && tabStyles.iconActive]}>
        {icons[label] || '\u25CF'}
      </Text>
    </View>
  );
}

const tabStyles = StyleSheet.create({
  iconWrap: { alignItems: 'center', justifyContent: 'center', paddingTop: 4 },
  icon: { fontSize: 20 },
  iconActive: { transform: [{ scale: 1.15 }] },
});

export default function RootLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: EMERALD,
        tabBarInactiveTintColor: INACTIVE,
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopColor: '#E8ECF0',
          borderTopWidth: 1,
          height: Platform.OS === 'ios' ? 88 : 64,
          paddingBottom: Platform.OS === 'ios' ? 28 : 8,
          paddingTop: 6,
          elevation: 8,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.06,
          shadowRadius: 8,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
          marginTop: 2,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ focused }) => <TabIcon label="Home" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="chat"
        options={{
          title: 'Chat',
          tabBarIcon: ({ focused }) => <TabIcon label="Chat" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="clients"
        options={{
          title: 'Clients',
          tabBarIcon: ({ focused }) => <TabIcon label="Clients" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="market"
        options={{
          title: 'Market',
          tabBarIcon: ({ focused }) => <TabIcon label="Market" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="alerts"
        options={{
          title: 'Alerts',
          tabBarIcon: ({ focused }) => <TabIcon label="Alerts" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="client/[id]"
        options={{
          href: null,
        }}
      />
    </Tabs>
  );
}
