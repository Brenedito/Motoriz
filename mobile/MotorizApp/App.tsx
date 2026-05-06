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
import React from 'react';
import { Documentos } from './src/screens/Documentos';
import { styles } from './src/styles/DashboardStyle';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator();

function App() {
  const isDarkMode = useColorScheme() === 'dark';
  const data = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  });

  const tabBarStyle = {
    tabBarStyle: {
      backgroundColor: '#192f53',
      height: 70,
      paddingBottom: 10,
      paddingTop: 10,
      borderTopWidth: 0,
      elevation: 10,
      shadowOpacity: 0.3,
    },
    tabBarActiveTintColor: '#fff',
    tabBarInactiveTintColor: '#b5bcc2',
    tabBarLabelStyle: {
      fontSize: 12,
      fontWeight: '600' as const,
    },
  };
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
              fontSize: 20,
              fontWeight: '500',
            },
            ...tabBarStyle,
          }}
        >
          <Tab.Screen
            name="DashboardVeiculos"
            component={DashboardVeiculos}
            options={{
              title: 'Motoriz',
              headerRight: () => (
                <Text style={styles.currentData}>Hoje, {data}</Text>
              ),
            }}
          />
          <Tab.Screen
            name="Documentos"
            component={Documentos}
            options={{
              title: 'Documentos',
              headerTitle: 'Meus Documentos',
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;
