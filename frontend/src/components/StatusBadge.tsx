import { clsx } from 'clsx';

interface Props {
  status: string;
}

export default function StatusBadge({ status }: Props) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold',
        {
          'bg-blue-100 text-blue-700': status === 'running' || status === 'pending',
          'bg-green-100 text-green-700': status === 'success',
          'bg-red-100 text-red-700': status === 'failed',
        }
      )}
    >
      {(status === 'running' || status === 'pending') && (
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
        </span>
      )}
      {status}
    </span>
  );
}
