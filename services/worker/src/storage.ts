export type ObjectStore = {
  download(bucket: string, path: string): Promise<Uint8Array>;
  upload(bucket: string, path: string, bytes: Uint8Array, contentType: string): Promise<void>;
};

function objectUrl(base: string, bucket: string, path: string): string {
  const encoded = path.split("/").map((part) => encodeURIComponent(part)).join("/");
  return `${base.replace(/\/$/, "")}/storage/v1/object/${bucket}/${encoded}`;
}

export function createStorage(url: string, secret: string): ObjectStore {
  return {
    async download(bucket, path) {
      const response = await fetch(objectUrl(url, bucket, path), {
        headers: { authorization: `Bearer ${secret}`, apikey: secret },
      });
      if (!response.ok) throw new Error("storage_download");
      return new Uint8Array(await response.arrayBuffer());
    },
    async upload(bucket, path, bytes, contentType) {
      const response = await fetch(objectUrl(url, bucket, path), {
        method: "POST",
        headers: {
          authorization: `Bearer ${secret}`,
          apikey: secret,
          "content-type": contentType,
          "x-upsert": "true",
        },
        body: Buffer.from(bytes),
      });
      if (!response.ok) throw new Error("storage_upload");
    },
  };
}
