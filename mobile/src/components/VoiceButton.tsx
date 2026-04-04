import React, { useRef, useState } from 'react';
import { TouchableOpacity, Text, StyleSheet, Animated, Alert, Platform } from 'react-native';
import { Audio } from 'expo-av';
import { sendVoice } from '../services/api';

interface VoiceButtonProps {
  onTranscription?: (response: string, toolsUsed: string[]) => void;
  disabled?: boolean;
}

export default function VoiceButton({ onTranscription, disabled }: VoiceButtonProps) {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [sending, setSending] = useState(false);
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const pulseRef = useRef<Animated.CompositeAnimation | null>(null);

  const startPulse = () => {
    pulseRef.current = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.15, duration: 600, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
      ])
    );
    pulseRef.current.start();
  };

  const stopPulse = () => {
    pulseRef.current?.stop();
    pulseAnim.setValue(1);
  };

  const startRecording = async () => {
    try {
      const { granted } = await Audio.requestPermissionsAsync();
      if (!granted) {
        Alert.alert('Permission required', 'Microphone access is needed to record voice.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording: rec } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(rec);
      startPulse();
    } catch (err) {
      console.error('Failed to start recording:', err);
      Alert.alert('Error', 'Could not start recording.');
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    stopPulse();

    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);

      if (uri) {
        setSending(true);
        try {
          const result = await sendVoice(uri);
          onTranscription?.(result.response, result.tools_used);
        } catch (err) {
          console.error('Voice send failed:', err);
          Alert.alert('Error', 'Could not process voice. Please try again.');
        } finally {
          setSending(false);
        }
      }
    } catch (err) {
      console.error('Failed to stop recording:', err);
      setRecording(null);
    }
  };

  const handlePress = () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const isActive = !!recording;

  return (
    <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
      <TouchableOpacity
        style={[
          styles.button,
          isActive && styles.buttonActive,
          sending && styles.buttonSending,
          disabled && styles.buttonDisabled,
        ]}
        onPress={handlePress}
        disabled={disabled || sending}
        activeOpacity={0.7}
      >
        <Text style={styles.icon}>{sending ? '\u23F3' : isActive ? '\u23F9' : '\uD83C\uDF99'}</Text>
        <Text style={styles.label}>
          {sending ? 'Processing...' : isActive ? 'Tap to stop' : 'Voice'}
        </Text>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#008C6F',
    borderRadius: 24,
    paddingHorizontal: 20,
    paddingVertical: 12,
    gap: 8,
    elevation: 3,
    shadowColor: '#008C6F',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  buttonActive: {
    backgroundColor: '#E53935',
  },
  buttonSending: {
    backgroundColor: '#666',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  icon: {
    fontSize: 18,
  },
  label: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});
