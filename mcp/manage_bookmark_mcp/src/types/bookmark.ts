export interface Bookmark {
  id: string;
  url: string;
  title: string;
  notes: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateBookmarkData {
  url: string;
  title: string;
  notes: string;
}
