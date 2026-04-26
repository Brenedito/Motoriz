import { FlatList, Text, TouchableOpacity, View } from 'react-native';
import { styles } from '../styles/DashboardStyle';
import { useEffect, useState } from 'react';
import { getVeiculos } from '../services/api';

const veiculos = [
  {
    id: 1,
    placa: 'ABC-1234',
    modelo: 'Fiat Argo 1.0',
    km: 15400,
    status: 'Disponível',
  },
  {
    id: 2,
    placa: 'DEF-5678',
    modelo: 'VW Polo Track',
    km: 8200,
    status: 'Alugado',
  },
  {
    id: 3,
    placa: 'GHI-9012',
    modelo: 'Chevrolet Onix',
    km: 22100,
    status: 'Em Manutenção',
  },
];

export function DashboardVeiculos() {
  // const [veiculos, setVeiculos] = useState([])

  // useEffect(() => {
  //   carregarVeiculos()
  // })

  // const carregarVeiculos = async () => {
  //   try {
  //     const response = await getVeiculos();
  //     setVeiculos(response.data);
  //   } catch (error) {
  //     console.error('Erro ao carregar veículos:', error);
  //   }
  // }
  const data = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  });
  const renderFooter = () => (
    <TouchableOpacity 
      style={styles.footerVerMaisVeiculos}
      onPress={() => console.log('Ver mais veículos')}
    >
      <Text style={styles.verMaisVeiculos}>
        Ver mais veículos
      </Text>
    </TouchableOpacity>
  )
  return (
    <View style={styles.container}>
      <View style={styles.navbar}>
        <Text style={styles.appTitle}>Motoriz</Text>
        <Text style={styles.currentData}>Hoje, {data}</Text>
      </View>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Visão Geral da Frota</Text>
        <View style={styles.containerInfos}>
          <View style={styles.infoCard}>
            <Text style={styles.cardLabel}>Locações Ativas</Text>
            <Text style={styles.cardValue}>2</Text>
            <Text style={styles.cardDescription}>
              40% de utilização de frota
            </Text>
          </View>
          <View style={styles.infoCard}>
            <Text style={styles.cardLabel}>Carros Disponíveis</Text>
            <Text style={styles.cardValue}>2</Text>
            <Text style={styles.cardDescription}>Prontos para locação</Text>
          </View>
          <View style={styles.infoCard}>
            <Text style={styles.cardLabel}>Em Manutenção</Text>
            <Text style={styles.cardValue}>1</Text>
            <Text style={styles.cardDescription}>Aguardando serviço</Text>
          </View>
          <View style={styles.infoCard}>
            <Text style={styles.cardLabel}>Pagamentos Pendentes</Text>
            <Text style={styles.cardValue}>1</Text>
            <Text style={styles.cardDescription}>De locações ativas</Text>
          </View>
        </View>
      </View>
      <View style={styles.veiculosContainer}>
        <View style={styles.veiculosHeader}>
          <Text style={styles.veiculosHeaderTitle}>Status Atual da Frota</Text>
        </View>

        <View style={styles.veiculosList}>
          <FlatList
            data={veiculos}
            keyExtractor={item => item.id.toString()}
            renderItem={({ item }) => (
              <View style={styles.veiculosCard}>
                <View style={styles.veiculosInfo}>
                  <Text style={styles.veiculosPlaca}>{item.placa}</Text>
                  <Text style={styles.veiculosModelo}>{item.modelo}</Text>
                  <Text style={styles.veiculosKm}>KM: {item.km}</Text>
                </View>
                <View style={styles.statusAndButtonLocalizar}>
                  <Text style={[styles.veiculosStatus, item.status === 'Alugado' && styles.statusAlugado, item.status === 'Disponível' && styles.statusDisponivel, item.status === 'Em Manutenção' && styles.statusManutencao]}>{item.status}</Text>
                  <TouchableOpacity style={styles.buttonLocalizar}>
                    <Text style={styles.Localizar}>Localizar</Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}
            ListFooterComponent={veiculos.length > 3 ? renderFooter : null}
          />
        </View>
      </View>
    </View>
  );
}
