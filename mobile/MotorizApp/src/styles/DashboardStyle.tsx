import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
    alignItems: 'center',
  },
  navbar: {
    flexDirection: 'row',
    width: '100%',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    alignItems: 'center',
    backgroundColor: '#192f53',
  },
  appTitle: {
    fontSize: 20,
    fontWeight: '500',
    color: '#FFF',
  },
  currentData: {
    color: '#b5bcc2',
    fontSize: 14,

    marginLeft: 'auto',
  },
  header: {
    padding: 16,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#fff',
    marginBottom: 16,
  },
  containerInfos: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  infoCard: {
    width: '48%',
    backgroundColor: '#192f53',
    borderRadius: 14,
    borderWidth: 1,
    padding: 14,
    borderColor: '#1f2f42'
  },
  cardLabel: {
    fontSize: 12.5,
    color: '#94A3B8',
    fontWeight: '600',
  },
  cardValue: {
    fontSize: 30,
    fontWeight: '800',
    color: '#E6EDF3',
  },
  cardDescription: {
    fontSize: 11,
    color: '#83898f',
  },
  veiculosContainer: {
    padding: 14,
    backgroundColor: '#192f53',
    width: '90%',
    borderRadius: 8,
  },
  veiculosHeader: {
    flexDirection: 'column',
    marginTop: 6,
    marginBottom: 17,
  },
  veiculosHeaderTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#fff',
  },
  veiculosList: {
    alignItems: 'center',
    fontSize: 14,
    color: '#b8bfc7',
    marginBottom: 12,
    width: '100%',
  },
  veiculosCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#1E293B',
    borderRadius: 10,
    paddingHorizontal: 18,
    paddingVertical: 10,
    marginBottom: 10,
    width: '100%',
    borderWidth: 1,
    borderColor: '#0b2b55',
  },
  veiculosInfo: {
    marginVertical: 4,
  },
  veiculosModelo: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    fontSize: 14,
    color: '#E6EDF3',
    fontWeight: '600',
    marginVertical: 5,
  },
  veiculosPlaca: {
    fontSize: 14,
    color: '#E2E8F0',
    backgroundColor: '#334155',
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignSelf: 'flex-start',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 4,
  },
  veiculosKm: {
    fontSize: 11,
    color: '#83898f',
  },
  statusAndButtonLocalizar: {
    flexDirection: 'column',
    alignItems: 'center',
  },
  veiculosStatus: {
    fontSize: 12,
    fontWeight: '600',
    color: '#22C55E',
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
  },
  buttonLocalizar: {
    marginTop: 27,
    backgroundColor: '#334155',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  Localizar: {
    fontSize: 14,
    color: '#E6EDF3',
  },
  footerVerMaisVeiculos: {
    padding: 12,
    alignItems: 'center',
  },
  verMaisVeiculos: {
    color: '#22C55E',
    fontSize: 14,
    fontWeight: '600',
    marginVertical: 10,
  },
  statusDisponivel: {
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
    color: '#22C55E'
  },
  statusAlugado: {
    color: '#3B82F6',
    backgroundColor: 'rgba(59, 130, 246, 0.15)'
  }, 
  statusManutencao: {
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
    color: '#F59E0B',
  }
});
