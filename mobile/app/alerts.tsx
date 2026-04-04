import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AlertItem from '../src/components/AlertItem';
import { fetchAlerts, AlertData } from '../src/services/api';

const TEAL = '#003235';
const EMERALD = '#008C6F';
const MINT = '#63D2B7';

type FilterType = 'all' | 'critical' | 'important' | 'info';

export default function AlertsScreen() {
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterType>('all');

  const load = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);
      const data = await fetchAlerts(50);
      setAlerts(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err.message || 'Failed to load alerts');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = filter === 'all' ? alerts : alerts.filter((a) => a.priority === filter);

  const counts = {
    all: alerts.length,
    critical: alerts.filter((a) => a.priority === 'critical').length,
    important: alerts.filter((a) => a.priority === 'important').length,
    info: alerts.filter((a) => a.priority === 'info').length,
  };

  if (loading && alerts.length === 0) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={EMERALD} />
        <Text style={styles.loadingText}>Loading alerts...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Alerts</Text>
        <Text style={styles.headerCount}>{alerts.length} total</Text>
      </View>

      {/* Filter Chips */}
      <View style={styles.filtersWrap}>
        {(['all', 'critical', 'important', 'info'] as FilterType[]).map((f) => {
          const isActive = filter === f;
          const chipColors: Record<string, string> = {
            all: EMERALD,
            critical: '#E53935',
            important: '#F9A825',
            info: '#1E88E5',
          };
          return (
            <TouchableOpacity
              key={f}
              style={[
                styles.chip,
                isActive && { backgroundColor: chipColors[f] },
              ]}
              onPress={() => setFilter(f)}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.chipText,
                  isActive && styles.chipTextActive,
                ]}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)} ({counts[f]})
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Error */}
      {error && (
        <TouchableOpacity style={styles.errorBanner} onPress={() => load()}>
          <Text style={styles.errorText}>{error}</Text>
          <Text style={styles.errorRetry}>Tap to retry</Text>
        </TouchableOpacity>
      )}

      {/* List */}
      <FlatList
        data={filtered}
        keyExtractor={(item, idx) => item.id || String(idx)}
        renderItem={({ item }) => <AlertItem alert={item} />}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor={EMERALD} />
        }
        ListEmptyComponent={
          <View style={styles.emptyWrap}>
            <Text style={styles.emptyText}>
              {filter !== 'all' ? `No ${filter} alerts` : 'No alerts'}
            </Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: TEAL },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' },
  loadingText: { marginTop: 12, color: '#666', fontSize: 14 },

  header: {
    backgroundColor: TEAL,
    paddingHorizontal: 20,
    paddingBottom: 14,
    paddingTop: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  headerTitle: { color: '#FFF', fontSize: 20, fontWeight: '800' },
  headerCount: { color: MINT, fontSize: 13, fontWeight: '500' },

  filtersWrap: {
    flexDirection: 'row',
    backgroundColor: '#F5F7FA',
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 8,
  },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  chipText: { fontSize: 12, fontWeight: '600', color: '#666' },
  chipTextActive: { color: '#FFFFFF' },

  errorBanner: {
    backgroundColor: '#FFEBEE',
    padding: 14,
    marginHorizontal: 16,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#E53935',
  },
  errorText: { color: '#C62828', fontSize: 13, fontWeight: '500' },
  errorRetry: { color: '#E53935', fontSize: 12, marginTop: 4, fontWeight: '600' },

  list: {
    paddingTop: 8,
    paddingBottom: 20,
    backgroundColor: '#F5F7FA',
    flexGrow: 1,
  },

  emptyWrap: { padding: 40, alignItems: 'center' },
  emptyText: { color: '#999', fontSize: 14, fontStyle: 'italic' },
});
