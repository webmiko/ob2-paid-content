import type { Post } from "../api/types";
import { useAuth } from "../context/AuthContext";
import { userNickname } from "../utils/avatar";
import { shouldProtectPaidContent } from "../utils/paidContent";
import PaidContentGuard from "./PaidContentGuard";

interface ProtectedPaidPostProps {
  post: Post;
  children: React.ReactNode;
}

/** Оборачивает платный контент защитой от копирования (кроме автора). */
export default function ProtectedPaidPost({ post, children }: ProtectedPaidPostProps) {
  const { user } = useAuth();
  const enabled = shouldProtectPaidContent(post, user?.id);
  const watermark = user ? `Creavity · ${userNickname(user.display_name)}` : "Creavity · платный контент";

  return (
    <PaidContentGuard enabled={enabled} watermark={enabled ? watermark : undefined}>
      {children}
    </PaidContentGuard>
  );
}
