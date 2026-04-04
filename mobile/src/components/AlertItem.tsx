import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AlertData } from '../services/api';
import { formatTimeAgo } from '../utils/format';

const PRIORITY_COLORS: Record<string, string> = {
  critical: '#E53935',
  important: '#F9A825',
  info: '#1E88E5',
};

const PRIORITY_BG: Record<string, string> = {
  critical: '#FFEBEE',
  important: '#FFF8E1',
  info: '#E3F2FD',
};

interface AlertItemProps {
  alert: AlertData;
}

export default function AlertItem({ alert }: AlertItemProps) {
  const color = PRIORITY_COLORS[alert.priority] || '#1E88E5';
  const bg = PRIORITY_BG[alert.priority] || '#E3F2FD';

  return (
    <View style={styles.card}>
      <View style={[styles.indicator, { backgroundColor: color }]} />
      <View style={styles.content}>
        <View style={styles.topRow}>
          <View style={[styles.badge, { backgroundColor: bg }]}>
            <Text style={[styles.badgeText, { color }]}>
              {alert.priority.toUpperCase()}
            </Text>
          </View>
          <Text style={styles.time}>{formatTimeAgo(alert.timestamp)}</Text>
        </View>
        <Text style={styles.title} numberOfLines={2}>{alert.title}</Text>
        {alert.description ? (
          <Text style={styles.description} numberOfLines={2}>{alert.description}</Text>
        ) : null}
        {alert.client_name ? (
          <Text style={styles.client}>{alert.client_name}</Text>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginHorizontal: 16,
    marginBottom: 10,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  indicator: {
    width: 5,
  },
  content: {
    flex: 1,
    padding: 14,
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  badge: {
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  time: {
    fontSize: 11,
    color: '#999',
  },
  title: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  description: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
  },
  client: {
    fontSize: 12,
    color: '#008C6F',
    marginTop: 4,
    fontWeight: '500',
  },
});
