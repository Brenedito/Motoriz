/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 */
import 'react-native-gesture-handler';
import { StatusBar, Text, useColorScheme } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { DashboardVeiculos } from './src/screens/DashboardVeiculos';
import React from 'react';
import { Documentos } from './src/screens/Documentos';
import { styles } from './src/styles/DashboardStyle';

const Drawer = createDrawerNavigator();

function App() {
  const isDarkMode = useColorScheme() === 'dark';
  const data = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  });
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
        <Drawer.Navigator
          initialRouteName="DashboardVeiculos"
          screenOptions={{
            headerShown: true,
            headerStyle: { backgroundColor: '#192f53' },
            headerTitle: 'Motoriz',
          }}
        >
          <Drawer.Screen
            name="DashboardVeiculos"
            component={DashboardVeiculos}
            options={{
              title: 'Dashboard',
              headerRight: () => (
                <Text style={styles.currentData}>
                  Hoje, {data}
                </Text>
              ),
             }}
          />
          <Drawer.Screen
            name="Documentos"
            component={Documentos}
            options={{
              title: 'Documentos'
              
            }}
          />
        </Drawer.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;
