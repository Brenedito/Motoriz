import {
  FlatList,
  Text,
  TextStyle,
  TouchableOpacity,
  View,
  ViewStyle,
} from 'react-native';
import { styles } from '../styles/DashboardStyle';
import { useEffect, useMemo, useState } from 'react';
import { getVeiculos } from '../services/api';

type statusVeiculo = 'DISPONIVEL' | 'ALUGADO' | 'MANUTENCAO';

export interface Veiculo {
  id: string | number;
  placa: string;
  modelo: string;
  quilometragemAtual: number;
  status: statusVeiculo;
}

interface StatusConfig {
  label: string;
  style: TextStyle | ViewStyle;
}

export function DashboardVeiculos() {
  const [veiculos, setVeiculos] = useState<Veiculo[]>([]);

  useEffect(() => {
    carregarVeiculos();
  }, []);

  const carregarVeiculos = async () => {
    try {
      const response = await getVeiculos();
      setVeiculos(response.data);
    } catch (error) {
      console.error('Erro ao carregar veículos:', error);
    }
  };
  const data = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  });
  const renderFooter = () => (
    <TouchableOpacity
      style={styles.footerVerMaisVeiculos}
    >
      <Text style={styles.verMaisVeiculos}>Ver mais veículos</Text>
    </TouchableOpacity>
  );

  const STATUS_CFG: Record<Veiculo['status'], StatusConfig> = {
    DISPONIVEL: { label: 'Disponível', style: styles.statusDisponivel },
    ALUGADO: { label: 'Alugado', style: styles.statusAlugado },
    MANUTENCAO: { label: 'Em Manutenção', style: styles.statusManutencao },
  };

  const statsVeiculos = useMemo(() => {
    const total = veiculos.length;
    const disponiveis = veiculos.filter(v => v.status === 'DISPONIVEL').length;
    const alugados = veiculos.filter(v => v.status === 'ALUGADO').length;
    const manutencao = veiculos.filter(v => v.status === 'MANUTENCAO').length;
    return {
      total,
      disponiveis,
      alugados,
      manutencao,
    };
  }, [veiculos]);

  const porcentagem = useMemo(() => {
    return statsVeiculos.total > 0
      ? Math.round((statsVeiculos.alugados / statsVeiculos.total) * 100)
      : 0;
  }, [statsVeiculos])

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
            <Text style={styles.cardValue}>{statsVeiculos.total}</Text>
            <Text style={styles.cardDescription}>
              {porcentagem}% de utilização de frota
            </Text>
          </View>
          <View style={styles.infoCard}>
            <Text style={styles.cardLabel}>Carros Disponíveis</Text>
            <Text style={styles.cardValue}>{statsVeiculos.disponiveis}</Text>
            <Text style={styles.cardDescription}>Prontos para locação</Text>
          </View>
          <View style={styles.infoCard}>
            <Text style={styles.cardLabel}>Em Manutenção</Text>
            <Text style={styles.cardValue}>{statsVeiculos.manutencao}</Text>
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
            renderItem={({ item }) => {
              const config = STATUS_CFG[item.status];
              return (
                <View style={styles.veiculosCard}>
                  <View style={styles.veiculosInfo}>
                    <Text style={styles.veiculosPlaca}>{item.placa}</Text>
                    <Text style={styles.veiculosModelo}>{item.modelo}</Text>
                    <Text style={styles.veiculosKm}>
                      KM: {item.quilometragemAtual}
                    </Text>
                  </View>
                  <View style={styles.statusAndButtonLocalizar}>
                    <Text style={[styles.veiculosStatus, config.style]}>
                      {config.label}
                    </Text>
                    <TouchableOpacity style={styles.buttonLocalizar}>
                      <Text style={styles.Localizar}>Localizar</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              );
            }}
            ListFooterComponent={veiculos.length > 3 ? renderFooter : null}
          />
        </View>
      </View>
    </View>
  );
}
