import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import FeedPage from "./pages/FeedPage";

const AuthorPage = lazy(() => import("./pages/AuthorPage"));
const ExplorePage = lazy(() => import("./pages/ExplorePage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const PaymentCancelPage = lazy(() => import("./pages/PaymentCancelPage"));
const PaymentSuccessPage = lazy(() => import("./pages/PaymentSuccessPage"));
const PostDetailPage = lazy(() => import("./pages/PostDetailPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const TopicPage = lazy(() => import("./pages/TopicPage"));

function PageFallback() {
  return <p className="loading-text">Загрузка…</p>;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<PageFallback />}>
            <Routes>
              <Route element={<Layout />}>
                <Route index element={<FeedPage />} />
                <Route path="explore" element={<ExplorePage />} />
                <Route path="authors/:id" element={<AuthorPage />} />
                <Route path="topics/:slug" element={<TopicPage />} />
                <Route path="posts/:id" element={<PostDetailPage />} />
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<RegisterPage />} />
                <Route path="profile" element={<ProfilePage />} />
                <Route path="payment/success" element={<PaymentSuccessPage />} />
                <Route path="payment/cancel" element={<PaymentCancelPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
