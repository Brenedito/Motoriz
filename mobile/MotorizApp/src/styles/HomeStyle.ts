import { StyleSheet } from 'react-native';

export const HomeStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    letterSpacing: 1.5,
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  mainContent: {
    flex: 1,
    paddingVertical: 24,
    paddingHorizontal: 16,
  },
  heroSection: {
    marginBottom: 32,
  },
  heroTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
    letterSpacing: 1,
    textAlign: 'center',
  },
  heroDescription: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
    marginBottom: 24,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 16,
    justifyContent: 'center',
  },
  featuresSection: {
    marginBottom: 32,
  },
  featuresSectionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 24,
  },
  featuresGrid: {
    gap: 16,
  },
  featureCard: {
    backgroundColor: '#1a1a1a',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  featureCardTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  featureCardText: {
    fontSize: 12,
    color: '#999',
  },
  ctaSection: {
    backgroundColor: '#1a1a1a',
    padding: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  ctaTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
    textAlign: 'center',
  },
  ctaDescription: {
    fontSize: 14,
    color: '#999',
    marginBottom: 16,
    textAlign: 'center',
  },
  footer: {
    paddingVertical: 24,
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: '#333',
    alignItems: 'center',
  },
  footerText: {
    fontSize: 11,
    color: '#666',
    marginBottom: 4,
  },
});
