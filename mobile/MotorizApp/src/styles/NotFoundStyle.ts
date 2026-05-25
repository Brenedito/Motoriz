import { StyleSheet } from 'react-native';

export const NotFoundStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  card: {
    backgroundColor: 'rgba(26, 26, 26, 0.8)',
    borderRadius: 12,
    paddingVertical: 32,
    paddingHorizontal: 24,
    alignItems: 'center',
    maxWidth: 400,
    width: '100%',
  },
  iconContainer: {
    marginBottom: 24,
    alignItems: 'center',
  },
  iconWrapper: {
    backgroundColor: 'rgba(255, 68, 68, 0.2)',
    borderRadius: 50,
    padding: 16,
  },
  icon: {
    fontSize: 64,
    color: '#ff4444'
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#ccc',
    marginBottom: 16,
  },
  description: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 22,
  },
  buttonGroup: {
    gap: 12,
    width: '100%',
  },
  button: {
    backgroundColor: '#0066cc',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});
