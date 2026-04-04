import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { formatPercent, formatINRAbsolute } from '../utils/format';

interface MarketCardProps {
  name: string;
  value: number;
  changePct: number;
  change?: number;
}

export default function MarketCard({ name, value, changePct, change }: MarketCardProps) {
  const isPositive = changePct >= 0;
  const changeColor = isPositive ? '#2E7D32' : '#C62828';
  const changeBg = isPositive ? '#E8F5E9' : '#FFEBEE';
  const arrow = isPositive ? '\u25B2' : '\u25BC';

  return (
    <View style={styles.card}>
      <Text style={styles.name}>{name}</Text>
      <Text style={styles.value}>{formatINRAbsolute(value)}</Text>
      <View style={[styles.changeRow, { backgroundColor: changeBg }]}>
        <Text style={[styles.changeText, { color: changeColor }]}>
          {arrow} {change != null ? formatINRAbsolute(Math.abs(change)) : ''}{' '}
          ({formatPercent(changePct)})
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    flex: 1,
    minWidth: 150,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  name: {
    fontSize: 13,
    color: '#666',
    fontWeight: '500',
    marginBottom: 6,
  },
  value: {
    fontSize: 20,
    fontWeight: '700',
    color: '#003235',
    marginBottom: 8,
  },
  changeRow: {
    alignSelf: 'flex-start',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  changeText: {
    fontSize: 12,
    fontWeight: '600',
  },
});
