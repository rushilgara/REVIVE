import React from 'react';

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = 'h-4 w-full' }) => {
  return <div className={`animate-pulse bg-slate-200/80 rounded ${className}`} />;
};

export const TableRowSkeleton: React.FC<{ cols?: number }> = ({ cols = 6 }) => {
  return (
    <tr className="border-b border-border/50">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="py-3 px-4">
          <Skeleton className="h-4 w-3/4" />
        </td>
      ))}
    </tr>
  );
};
