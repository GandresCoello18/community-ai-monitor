import { Badge, Card } from "@/components/ui";
import { CameraPreview } from "@/components/cameras/CameraPreview";
import { QueryPanel } from "@/components/common/QueryPanel";
import { useCameras } from "@/hooks/useCameras";
import { useStreamStatuses } from "@/hooks/useStreamStatuses";
import type { StreamStatus } from "@/types/api";
import { formatDateTime, streamStatusVariant } from "@/utils/format";

export function CamerasPage() {
  const camerasQuery = useCameras();
  const streamsQuery = useStreamStatuses();

  const cameras = camerasQuery.data?.data ?? [];
  const streamMap = new Map<string, StreamStatus>(
    (streamsQuery.data ?? []).map((stream) => [stream.camera_id, stream]),
  );

  const isLoading = camerasQuery.isLoading || streamsQuery.isLoading;
  const error = camerasQuery.error ?? streamsQuery.error;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Cámaras</h1>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Vista en vivo y estado de las cámaras que analiza el sistema.
        </p>
      </div>

      <QueryPanel
        isLoading={isLoading}
        error={error}
        isEmpty={cameras.length === 0}
        emptyTitle="No hay cámaras registradas"
        emptyDescription="Agrega cámaras desde la API o activa SEED_DEMO_DATA en el backend."
      >
        <div className="grid gap-6 lg:grid-cols-2">
          {cameras.map((camera) => {
            const stream = streamMap.get(camera.id);
            const isRunning = stream?.status === "running";

            return (
              <Card key={camera.id} className="overflow-hidden p-0">
                <div className="p-4 pb-0">
                  <CameraPreview
                    cameraId={camera.id}
                    cameraName={camera.name}
                    isStreamRunning={isRunning}
                  />
                </div>
                <div className="space-y-3 p-5">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <h3 className="font-semibold">{camera.name}</h3>
                      <p className="text-sm text-[var(--color-muted)]">
                        {camera.location}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant={camera.is_active ? "success" : "default"}>
                        {camera.is_active ? "Activa" : "Inactiva"}
                      </Badge>
                      {stream ? (
                        <Badge variant={streamStatusVariant(stream.status)}>
                          {stream.status}
                        </Badge>
                      ) : null}
                    </div>
                  </div>
                  <dl className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <dt className="text-[var(--color-muted)]">Detecciones</dt>
                      <dd className="font-medium">
                        {stream?.detections_processed ?? 0}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-[var(--color-muted)]">Último frame</dt>
                      <dd className="font-medium">
                        {formatDateTime(stream?.last_frame_at)}
                      </dd>
                    </div>
                  </dl>
                </div>
              </Card>
            );
          })}
        </div>
      </QueryPanel>
    </div>
  );
}
