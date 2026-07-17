import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Wallet from "./pages/Wallet";
import GetPaid from "./pages/GetPaid";
import Pay from "./pages/Pay";
import PayConfirm from "./pages/PayConfirm";
import PaySuccess from "./pages/PaySuccess";
import KycUpload from "./pages/KycUpload";
import AdminDisclose from "./pages/AdminDisclose";
import AdminKycReview from "./pages/AdminKycReview";
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
          path="/kyc"
          element={
            <ProtectedRoute>
              <KycUpload />
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
        <Route
          path="/admin/disclose"
          element={
            <ProtectedRoute>
              <AdminDisclose />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/kyc/review"
          element={
            <ProtectedRoute>
              <AdminKycReview />
            </ProtectedRoute>
          }
        />  
      </Routes>
    </BrowserRouter>
  );
}