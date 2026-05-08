/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 */
import 'react-native-gesture-handler';
import { StatusBar, Text, useColorScheme } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { DashboardVeiculos } from './src/screens/DashboardVeiculos';
import React, { useMemo } from 'react';
import { Documentos } from './src/screens/Documentos';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { tabOptions } from './src/styles/GlobalStyle';

const Tab = createBottomTabNavigator();

interface HeaderDateProps {
  data: string;
}

const HeaderDate = ({ data }: HeaderDateProps) => (
  <Text style={{ color: '#b5bcc2', fontSize: 14, marginRight: 10 }}>
    Hoje, {data}
  </Text>
);

function App() {
  const isDarkMode = useColorScheme() === 'dark';
  const dataAtual = useMemo(() => {
    return new Date().toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
    });
  }, [])
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
        <Tab.Navigator
          screenOptions={{
            headerShown: true,
            headerStyle: { backgroundColor: '#192f53' },
            headerTitleStyle: {
              color: '#fff',
            },
            headerRight: () => <HeaderDate data={dataAtual} />,
            ...tabOptions,
          }}
        >
          <Tab.Screen name="Dashboard" component={DashboardVeiculos} />
          <Tab.Screen name="Documentos" component={Documentos} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;
