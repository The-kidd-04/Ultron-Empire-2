import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { fetchDashboard, DashboardData } from '../src/services/api';
import { formatINR, formatDate } from '../src/utils/format';

const TEAL = '#003235';
const EMERALD = '#008C6F';
const MINT = '#63D2B7';

export default function HomeTab() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);
      const data = await fetchDashboard();
      setDashboard(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading && !dashboard) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={EMERALD} />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor={EMERALD} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.logo}>Ultron Empire</Text>
          <Text style={styles.subtitle}>PMS Sahi Hai</Text>
        </View>
        <View style={styles.headerBadge}>
          <Text style={styles.headerBadgeText}>LIVE</Text>
        </View>
      </View>

      {/* Error Banner */}
      {error && (
        <TouchableOpacity style={styles.errorBanner} onPress={() => load()}>
          <Text style={styles.errorText}>{error}</Text>
          <Text style={styles.errorRetry}>Tap to retry</Text>
        </TouchableOpacity>
      )}

      {/* Stats Row */}
      <View style={styles.cardRow}>
        <StatCard title="Total AUM" value={formatINR(dashboard?.aum?.total_cr)} />
        <StatCard title="Clients" value={String(dashboard?.aum?.client_count ?? '--')} />
      </View>

      <View style={styles.cardRow}>
        <StatCard
          title="Critical Alerts"
          value={String(dashboard?.alerts?.critical ?? 0)}
          accentColor="#E53935"
        />
        <StatCard
          title="Important"
          value={String(dashboard?.alerts?.important ?? 0)}
          accentColor="#F9A825"
        />
        <StatCard
          title="Info"
          value={String(dashboard?.alerts?.info ?? 0)}
          accentColor="#1E88E5"
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsRow}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => router.push('/chat')}>
          <Text style={styles.actionIcon}>{'\uD83D\uDCAC'}</Text>
          <Text style={styles.actionLabel}>Ask Ultron</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => router.push('/clients')}>
          <Text style={styles.actionIcon}>{'\uD83D\uDC65'}</Text>
          <Text style={styles.actionLabel}>Clients</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => router.push('/market')}>
          <Text style={styles.actionIcon}>{'\uD83D\uDCC8'}</Text>
          <Text style={styles.actionLabel}>Market</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => router.push('/alerts')}>
          <Text style={styles.actionIcon}>{'\uD83D\uDD14'}</Text>
          <Text style={styles.actionLabel}>Alerts</Text>
        </TouchableOpacity>
      </View>

      {/* Recent Alerts */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Alerts</Text>
          <TouchableOpacity onPress={() => router.push('/alerts')}>
            <Text style={styles.seeAll}>See all</Text>
          </TouchableOpacity>
        </View>
        {(dashboard?.alerts?.recent || []).length === 0 && (
          <Text style={styles.emptyText}>No recent alerts</Text>
        )}
        {(dashboard?.alerts?.recent || []).slice(0, 5).map((a, i) => (
          <View key={i} style={styles.alertItem}>
            <View
              style={[
                styles.alertDot,
                {
                  backgroundColor:
                    a.priority === 'critical' ? '#E53935' : a.priority === 'important' ? '#F9A825' : '#1E88E5',
                },
              ]}
            />
            <View style={styles.alertContent}>
              <Text style={styles.alertTitle} numberOfLines={1}>{a.title}</Text>
              {a.description ? (
                <Text style={styles.alertDesc} numberOfLines={1}>{a.description}</Text>
              ) : null}
            </View>
          </View>
        ))}
      </View>

      {/* Overdue Reviews */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Overdue Reviews</Text>
          <Text style={styles.badge}>{dashboard?.reviews?.overdue_count ?? 0}</Text>
        </View>
        {(dashboard?.reviews?.overdue_clients || []).length === 0 && (
          <Text style={styles.emptyText}>All reviews are on track</Text>
        )}
        {(dashboard?.reviews?.overdue_clients || []).slice(0, 5).map((c, i) => (
          <View key={i} style={styles.reviewItem}>
            <Text style={styles.reviewName}>{c.name}</Text>
            <Text style={styles.reviewDue}>Due: {formatDate(c.due)}</Text>
          </View>
        ))}
      </View>

      <View style={{ height: 30 }} />
    </ScrollView>
  );
}

function StatCard({
  title,
  value,
  accentColor,
}: {
  title: string;
  value: string;
  accentColor?: string;
}) {
  return (
    <View style={[styles.card, { borderLeftColor: accentColor || EMERALD }]}>
      <Text style={styles.cardLabel}>{title}</Text>
      <Text style={[styles.cardValue, accentColor ? { color: accentColor } : {}]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F7FA' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' },
  loadingText: { marginTop: 12, color: '#666', fontSize: 14 },

  header: {
    backgroundColor: TEAL,
    paddingHorizontal: 20,
    paddingTop: 56,
    paddingBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  logo: { color: '#FFFFFF', fontSize: 24, fontWeight: '800', letterSpacing: 0.5 },
  subtitle: { color: MINT, fontSize: 12, marginTop: 2, fontWeight: '500' },
  headerBadge: {
    backgroundColor: '#E53935',
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  headerBadgeText: { color: '#FFF', fontSize: 10, fontWeight: '800', letterSpacing: 1 },

  errorBanner: {
    backgroundColor: '#FFEBEE',
    padding: 14,
    marginHorizontal: 16,
    marginTop: 12,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#E53935',
  },
  errorText: { color: '#C62828', fontSize: 13, fontWeight: '500' },
  errorRetry: { color: '#E53935', fontSize: 12, marginTop: 4, fontWeight: '600' },

  cardRow: { flexDirection: 'row', paddingHorizontal: 12, paddingTop: 10, gap: 10 },
  card: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
  },
  cardLabel: { fontSize: 11, color: '#8E9BAE', fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.5 },
  cardValue: { fontSize: 22, fontWeight: '800', color: TEAL, marginTop: 6 },

  actionsRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingTop: 18,
    gap: 10,
  },
  actionBtn: {
    flex: 1,
    backgroundColor: EMERALD,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  actionIcon: { fontSize: 22, marginBottom: 4 },
  actionLabel: { color: '#FFF', fontSize: 11, fontWeight: '600' },

  section: { paddingHorizontal: 16, paddingTop: 22 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: TEAL },
  seeAll: { fontSize: 13, color: EMERALD, fontWeight: '600' },
  badge: {
    backgroundColor: '#E53935',
    color: '#FFF',
    fontSize: 12,
    fontWeight: '700',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    overflow: 'hidden',
  },
  emptyText: { color: '#999', fontSize: 13, fontStyle: 'italic' },

  alertItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
  },
  alertDot: { width: 10, height: 10, borderRadius: 5, marginRight: 12 },
  alertContent: { flex: 1 },
  alertTitle: { fontSize: 14, fontWeight: '600', color: '#1A1A1A' },
  alertDesc: { fontSize: 12, color: '#666', marginTop: 2 },

  reviewItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
  },
  reviewName: { fontSize: 14, fontWeight: '600', color: '#1A1A1A' },
  reviewDue: { fontSize: 12, color: '#E53935', fontWeight: '500' },
});
