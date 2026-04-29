import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900">
      <div className="text-center">
        <div className="text-8xl font-bold text-slate-200 dark:text-slate-700 mb-4">404</div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">
          Page not found
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mb-6">
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
        <Link href="/" className="btn-primary">
          Go Home
        </Link>
      </div>
    </div>
  );
}
