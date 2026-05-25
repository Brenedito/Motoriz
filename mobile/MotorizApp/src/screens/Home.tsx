import { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { useLocation } from "wouter";
import { HomeStyles } from '../styles/HomeStyle';

export default function Home() {
  const [, setLocation] = useLocation();

  return (
    <View style={HomeStyles.container}>
      {/* Header */}
      <View style={HomeStyles.header}>
        <Text style={HomeStyles.logo}>MOTORIZ</Text>
        <View style={HomeStyles.headerButtons}>
          <TouchableOpacity onPress={() => setLocation("/login")}>
            <Text style={{ color: '#fff', fontSize: 14 }}>Login</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={() => setLocation("/register")}>
            <Text style={{ color: '#fff', fontSize: 14, fontWeight: '600' }}>Cadastro</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Main Content */}
      <ScrollView style={HomeStyles.mainContent} showsVerticalScrollIndicator={false}>
        {/* Hero Section */}
        <View style={HomeStyles.heroSection}>
          <Text style={HomeStyles.heroTitle}>
            SISTEMA DE{'\n'}AUTENTICAÇÃO
          </Text>
          <Text style={HomeStyles.heroDescription}>
            Plataforma premium de gestão para locadora de carros. Acesso seguro, interface intuitiva e controle total da sua frota.
          </Text>
          <View style={HomeStyles.buttonContainer}>
            <TouchableOpacity onPress={() => setLocation("/login")}>
              <Text style={{ color: '#fff', fontWeight: '600' }}>[ ACESSAR SISTEMA ]</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setLocation("/register")}>
              <Text style={{ color: '#fff', fontWeight: '600' }}>[ CRIAR CONTA ]</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Features Section */}
        <View style={HomeStyles.featuresSection}>
          <Text style={HomeStyles.featuresSectionTitle}>RECURSOS PREMIUM</Text>
          <View style={HomeStyles.featuresGrid}>
            <View style={HomeStyles.featureCard}>
              <Text style={HomeStyles.featureCardTitle}>SEGURANÇA</Text>
              <Text style={HomeStyles.featureCardText}>
                Autenticação segura com criptografia de ponta a ponta e proteção de dados em tempo real.
              </Text>
            </View>
            <View style={HomeStyles.featureCard}>
              <Text style={HomeStyles.featureCardTitle}>CONTROLE</Text>
              <Text style={HomeStyles.featureCardText}>
                Gestão completa de acessos, permissões e auditoria de atividades do sistema.
              </Text>
            </View>
            <View style={HomeStyles.featureCard}>
              <Text style={HomeStyles.featureCardTitle}>PERFORMANCE</Text>
              <Text style={HomeStyles.featureCardText}>
                Interface responsiva e otimizada para todos os dispositivos com carregamento instantâneo.
              </Text>
            </View>
          </View>
        </View>

        {/* CTA Section */}
        <View style={HomeStyles.ctaSection}>
          <Text style={HomeStyles.ctaTitle}>PRONTO PARA COMEÇAR?</Text>
          <Text style={HomeStyles.ctaDescription}>
            Crie sua conta agora e acesse o painel de controle completo da sua locadora de carros.
          </Text>
          <TouchableOpacity onPress={() => setLocation("/register")}>
            <Text style={{ color: '#fff', fontWeight: '600' }}>[ CRIAR CONTA AGORA ]</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Footer */}
      <View style={HomeStyles.footer}>
        <Text style={HomeStyles.footerText}>&gt; MOTORIZ_HOME_v2.0.1</Text>
        <Text style={HomeStyles.footerText}>&gt; STATUS: ONLINE</Text>
        <Text style={HomeStyles.footerText}>© 2026 MOTORIZ - Sistema de Autenticação Premium</Text>
      </View>
    </View>
  );
}
