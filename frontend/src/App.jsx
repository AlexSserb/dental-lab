import './App.css';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ApplicationBar from './components/AppBar';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import CreateOrderPage from './pages/CreateOrderPage';
import OperationsForProductPage from './pages/OperationsForProductPage';
import OrderPage from './pages/OrderPage';
import TechSchedule from './components/TechSchedule';
import OrderProcessingPage from './pages/OrderProcessingPage';
import AssignOperationsPage from './pages/AssingOperationsPage';

function App() {
  return (
    <div>
      <AuthProvider>
        <ApplicationBar/>
        <Routes>
          <Route exact path='/' element={<HomePage/>} />
          <Route path='/login' element={<LoginPage/>} />
          <Route path='/registration' element={<RegisterPage/>} />
          <Route path='/profile' element={<ProfilePage/>} />
          <Route path='/create-order' element={<CreateOrderPage/>} />
          <Route path='/process-order' element={<OrderProcessingPage/>} />
          <Route path='/assign-operations' element={<AssignOperationsPage/>} />
          <Route path='/operations-for-product' element={<OperationsForProductPage/>} />
          <Route path='/order' element={<OrderPage/>} />
          <Route path='/schedule' element={<TechSchedule/>} />
        </Routes>
      </AuthProvider>
    </div>
  );
}

export default App;
