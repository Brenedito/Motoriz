import 'react-native-gesture-handler';
import { Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { DashboardVeiculos } from './src/screens/DashboardVeiculos';
import React, { useMemo } from 'react';
import { Documentos } from './src/screens/Documentos';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { style, tabOptions } from './src/styles/GlobalStyle';
import { LayoutDashboard, FileText } from 'lucide-react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';


const Tab = createBottomTabNavigator();

interface HeaderDateProps {
  data: string;
}

const HeaderDate = ({ data }: HeaderDateProps) => (
  <Text style={style.headerDate}>
    Hoje, {data}
  </Text>
);

function App() {
  const dataAtual = useMemo(() => {
    return new Date().toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
    });
  }, [])
  return (
    <GestureHandlerRootView style={{flex: 1}}>
      <SafeAreaProvider>
      <NavigationContainer>
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
          <Tab.Screen name="Dashboard" component={DashboardVeiculos} options={{
            tabBarIcon: ({ color, size }: any) => (
              <LayoutDashboard color={color} size={size}/>
            )
          }}/>
          <Tab.Screen name="Documentos" component={Documentos} options={{
            tabBarIcon: ({ color, size }: any) => (
              <FileText color={color} size={size}/>
            )
          }}/>
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

export default App;