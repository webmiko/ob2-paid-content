import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import { AuthProvider } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import PaymentCancelPage from "./pages/PaymentCancelPage";
import PaymentSuccessPage from "./pages/PaymentSuccessPage";
import PostDetailPage from "./pages/PostDetailPage";
import PostsPage from "./pages/PostsPage";
import ProfilePage from "./pages/ProfilePage";
import RegisterPage from "./pages/RegisterPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<PostsPage />} />
            <Route path="posts/:id" element={<PostDetailPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="payment/success" element={<PaymentSuccessPage />} />
            <Route path="payment/cancel" element={<PaymentCancelPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
