import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Wallet from "./pages/Wallet";
import GetPaid from "./pages/GetPaid";
import Pay from "./pages/Pay";
import PayConfirm from "./pages/PayConfirm";
import PaySuccess from "./pages/PaySuccess";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/wallet"
          element={
            <ProtectedRoute>
              <Wallet />
            </ProtectedRoute>
          }
        />
        <Route
          path="/get-paid"
          element={
            <ProtectedRoute>
              <GetPaid />
            </ProtectedRoute>
          }
        />  
        <Route
          path="/pay"
          element={
            <ProtectedRoute>
              <Pay />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pay/confirm"
          element={
            <ProtectedRoute>
              <PayConfirm />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pay/success"
          element={
            <ProtectedRoute>
              <PaySuccess />
            </ProtectedRoute>
          }
        />  
      </Routes>
    </BrowserRouter>
  );
}