import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ClientSummary } from '../services/api';
import { formatINR } from '../utils/format';

const RISK_COLORS: Record<string, string> = {
  aggressive: '#E53935',
  'moderately aggressive': '#F57C00',
  moderate: '#F9A825',
  'moderately conservative': '#43A047',
  conservative: '#1E88E5',
};

interface ClientCardProps {
  client: ClientSummary;
  onPress?: () => void;
}

export default function ClientCard({ client, onPress }: ClientCardProps) {
  const riskColor = RISK_COLORS[client.risk_profile?.toLowerCase()] || '#008C6F';
  const initials = client.name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={[styles.avatar, { backgroundColor: riskColor + '20' }]}>
        <Text style={[styles.initials, { color: riskColor }]}>{initials}</Text>
      </View>
      <View style={styles.info}>
        <Text style={styles.name} numberOfLines={1}>{client.name}</Text>
        <Text style={styles.aum}>{formatINR(client.aum_cr)}</Text>
      </View>
      <View style={[styles.riskBadge, { backgroundColor: riskColor + '18' }]}>
        <Text style={[styles.riskText, { color: riskColor }]}>
          {client.risk_profile || 'N/A'}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginHorizontal: 16,
    marginBottom: 10,
    padding: 14,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  initials: {
    fontSize: 16,
    fontWeight: '700',
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  aum: {
    fontSize: 13,
    color: '#666',
    marginTop: 2,
  },
  riskBadge: {
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
    marginLeft: 8,
  },
  riskText: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
});
