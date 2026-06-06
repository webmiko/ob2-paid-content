interface PostBadgeProps {
  isPaid: boolean;
}

export default function PostBadge({ isPaid }: PostBadgeProps) {
  return (
    <span className={`badge-type ${isPaid ? "badge-premium" : "badge-free"}`}>
      {isPaid ? "Платная" : "Бесплатная"}
    </span>
  );
}
