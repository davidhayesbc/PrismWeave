/**
 * Shared utility functions
 */

export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

export function sanitizeFilename(filename: string): string {
  return filename.replace(/[^a-z0-9-_.]/gi, '-').toLowerCase();
}
