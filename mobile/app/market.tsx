import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import MarketCard from '../src/components/MarketCard';
import { fetchMarket, MarketOverview } from '../src/services/api';
import { formatPercent, formatDate } from '../src/utils/format';

const TEAL = '#003235';
const EMERALD = '#008C6F';
const MINT = '#63D2B7';

export default function MarketScreen() {
  const [market, setMarket] = useState<MarketOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);
      const data = await fetchMarket();
      setMarket(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load market data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading && !market) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={EMERALD} />
        <Text style={styles.loadingText}>Loading market data...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Market Overview</Text>
        {market?.updated_at && (
          <Text style={styles.headerSub}>Updated: {formatDate(market.updated_at)}</Text>
        )}
      </View>

      <ScrollView
        style={styles.body}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor={EMERALD} />
        }
      >
        {error && (
          <TouchableOpacity style={styles.errorBanner} onPress={() => load()}>
            <Text style={styles.errorText}>{error}</Text>
            <Text style={styles.errorRetry}>Tap to retry</Text>
          </TouchableOpacity>
        )}

        {/* VIX Banner */}
        {market?.vix != null && (
          <View style={[styles.vixBanner, market.vix > 20 ? styles.vixHigh : styles.vixNormal]}>
            <Text style={styles.vixLabel}>India VIX</Text>
            <Text style={styles.vixValue}>{market.vix.toFixed(2)}</Text>
            <Text style={styles.vixNote}>
              {market.vix > 25
                ? 'High volatility - Caution advised'
                : market.vix > 18
                ? 'Moderate volatility'
                : 'Low volatility - Stable market'}
            </Text>
          </View>
        )}

        {/* Indices */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Major Indices</Text>
          <View style={styles.cardGrid}>
            {(market?.indices || []).map((idx, i) => (
              <View key={i} style={styles.cardWrap}>
                <MarketCard
                  name={idx.name}
                  value={idx.value}
                  changePct={idx.change_pct}
                  change={idx.change}
                />
              </View>
            ))}
          </View>
          {(market?.indices || []).length === 0 && (
            <Text style={styles.emptyText}>No index data available</Text>
          )}
        </View>

        {/* Sector Performance */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sector Performance</Text>
          {(market?.sectors || []).length === 0 && (
            <Text style={styles.emptyText}>No sector data available</Text>
          )}
          {(market?.sectors || []).map((sector, i) => {
            const isPositive = sector.change_pct >= 0;
            return (
              <View key={i} style={styles.sectorRow}>
                <Text style={styles.sectorName}>{sector.name}</Text>
                <View
                  style={[
                    styles.sectorBadge,
                    { backgroundColor: isPositive ? '#E8F5E9' : '#FFEBEE' },
                  ]}
                >
                  <Text
                    style={[
                      styles.sectorChange,
                      { color: isPositive ? '#2E7D32' : '#C62828' },
                    ]}
                  >
                    {formatPercent(sector.change_pct)}
                  </Text>
                </View>
                {/* Mini bar */}
                <View style={styles.sectorBarWrap}>
                  <View
                    style={[
                      styles.sectorBar,
                      {
                        width: `${Math.min(Math.abs(sector.change_pct) * 10, 100)}%`,
                        backgroundColor: isPositive ? '#2E7D32' : '#C62828',
                      },
                    ]}
                  />
                </View>
              </View>
            );
          })}
        </View>

        <View style={{ height: 30 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: TEAL },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' },
  loadingText: { marginTop: 12, color: '#666', fontSize: 14 },
  body: { flex: 1, backgroundColor: '#F5F7FA' },

  header: {
    backgroundColor: TEAL,
    paddingHorizontal: 20,
    paddingBottom: 14,
    paddingTop: 8,
  },
  headerTitle: { color: '#FFF', fontSize: 20, fontWeight: '800' },
  headerSub: { color: MINT, fontSize: 12, fontWeight: '500', marginTop: 2 },

  errorBanner: {
    backgroundColor: '#FFEBEE',
    padding: 14,
    margin: 16,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#E53935',
  },
  errorText: { color: '#C62828', fontSize: 13, fontWeight: '500' },
  errorRetry: { color: '#E53935', fontSize: 12, marginTop: 4, fontWeight: '600' },

  vixBanner: {
    margin: 16,
    borderRadius: 14,
    padding: 18,
    alignItems: 'center',
  },
  vixNormal: { backgroundColor: '#E8F5E9' },
  vixHigh: { backgroundColor: '#FFF3E0' },
  vixLabel: { fontSize: 12, fontWeight: '600', color: '#666', textTransform: 'uppercase', letterSpacing: 0.5 },
  vixValue: { fontSize: 32, fontWeight: '800', color: TEAL, marginTop: 4 },
  vixNote: { fontSize: 13, color: '#666', marginTop: 6, fontWeight: '500' },

  section: { paddingHorizontal: 16, marginTop: 8 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: TEAL, marginBottom: 12 },
  emptyText: { color: '#999', fontSize: 13, fontStyle: 'italic' },

  cardGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  cardWrap: { width: '48%', marginBottom: 2 },

  sectorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
  },
  sectorName: { flex: 1, fontSize: 14, fontWeight: '600', color: '#1A1A1A' },
  sectorBadge: { borderRadius: 6, paddingHorizontal: 10, paddingVertical: 3, marginRight: 12 },
  sectorChange: { fontSize: 13, fontWeight: '700' },
  sectorBarWrap: { width: 60, height: 4, backgroundColor: '#E8ECF0', borderRadius: 2, overflow: 'hidden' },
  sectorBar: { height: '100%', borderRadius: 2 },
});
