import { BrowserRouter, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import AuthorPage from "./pages/AuthorPage";
import ExplorePage from "./pages/ExplorePage";
import FeedPage from "./pages/FeedPage";
import LoginPage from "./pages/LoginPage";
import PaymentCancelPage from "./pages/PaymentCancelPage";
import PaymentSuccessPage from "./pages/PaymentSuccessPage";
import PostDetailPage from "./pages/PostDetailPage";
import ProfilePage from "./pages/ProfilePage";
import RegisterPage from "./pages/RegisterPage";
import NotFoundPage from "./pages/NotFoundPage";
import TopicPage from "./pages/TopicPage";

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
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
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
