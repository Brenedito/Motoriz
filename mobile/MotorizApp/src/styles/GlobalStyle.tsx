import { BottomTabNavigationOptions } from "@react-navigation/bottom-tabs";
import { Colors } from "./Colors";

export const tabOptions: BottomTabNavigationOptions = {
    tabBarStyle: {
      backgroundColor: Colors.cardBackground,
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
      fontWeight: '600',
    },
}