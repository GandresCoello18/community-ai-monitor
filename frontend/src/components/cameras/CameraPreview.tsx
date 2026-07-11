import { useState } from "react";

import { getCameraPreviewStreamUrl } from "@/api/preview";
import { cn } from "@/utils/cn";

interface CameraPreviewProps {
  cameraId: string;
  cameraName: string;
  isStreamRunning: boolean;
  className?: string;
}

export function CameraPreview({
  cameraId,
  cameraName,
  isStreamRunning,
  className,
}: CameraPreviewProps) {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  if (!isStreamRunning) {
    return (
      <div
        className={cn(
          "flex aspect-video items-center justify-center rounded-[var(--radius-md)] border border-dashed border-[var(--color-border)] bg-[var(--color-surface-hover)]",
          className,
        )}
      >
        <p className="px-4 text-center text-sm text-[var(--color-muted)]">
          Stream detenido. Inicia la cámara para ver la vista previa.
        </p>
      </div>
    );
  }

  if (hasError) {
    return (
      <div
        className={cn(
          "flex aspect-video items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface-hover)]",
          className,
        )}
      >
        <p className="px-4 text-center text-sm text-[var(--color-muted)]">
          Vista previa no disponible todavía. Espera unos segundos mientras
          llega el primer frame.
        </p>
      </div>
    );
  }

  const streamUrl = getCameraPreviewStreamUrl(cameraId);

  return (
    <div
      className={cn(
        "relative aspect-video overflow-hidden rounded-[var(--radius-md)] border border-[var(--color-border)] bg-black",
        className,
      )}
    >
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[var(--color-surface-hover)]">
          <p className="text-sm text-[var(--color-muted)]">Cargando vista previa…</p>
        </div>
      )}
      <img
        src={streamUrl}
        alt={`Vista en vivo de ${cameraName}`}
        className="h-full w-full object-contain"
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setIsLoading(false);
          setHasError(true);
        }}
      />
      <div className="absolute bottom-2 left-2 rounded bg-black/60 px-2 py-1 text-xs text-white">
        En vivo
      </div>
    </div>
  );
}
