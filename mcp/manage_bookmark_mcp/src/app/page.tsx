"use client"
import { useState } from "react"
import { SignedIn, SignedOut } from "@clerk/nextjs"
import { useBookmarks } from "@/hooks/useBookmarks"
import type { CreateBookmarkData, Bookmark } from "@/types/bookmark"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import BookmarkForm from "@/components/BookmarkForm"
import BookmarkList from "@/components/BookmarkList"
import { Plus, Loader2 } from "lucide-react"

const Home = () => {
  const { addBookmark, updateBookmark, bookmarks, deleteBookmark, error, loading, refetch } = useBookmarks()

  const [showAddForm, setShowAddForm] = useState(false)
  const [showEditForm, setShowEditForm] = useState(false) // Added state for edit dialog
  const [editingBookmark, setEditingBookmark] = useState<Bookmark | null>(null) // Added state for bookmark being edited
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleAddBookmark = async (data: CreateBookmarkData) => {
    try {
      setIsSubmitting(true)
      await addBookmark(data)
      setShowAddForm(false)
    } catch (error) {
      console.log("Failed to add bookmark", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEditBookmark = async (data: CreateBookmarkData) => {
    if (!editingBookmark) return

    try {
      setIsSubmitting(true)
      await updateBookmark(editingBookmark.id, data)
      setShowEditForm(false)
      setEditingBookmark(null)
    } catch (error) {
      console.log("Failed to update bookmark", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEditClick = (bookmark: Bookmark) => {
    setEditingBookmark(bookmark)
    setShowEditForm(true)
  }

  const handleDeleteBookmark = async (id: string) => {
    if (confirm("Are you sure you want to delete this bookmark?")) {
      try {
        await deleteBookmark(id)
      } catch (error) {
        console.log("Failed to delete bookmark", error)
      }
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-12">
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-8">
      <SignedIn>
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">Your Bookmarks</h1>
              <p className="text-muted-foreground">Organize and manage your favorite links</p>
            </div>
            <Dialog open={showAddForm} onOpenChange={setShowAddForm}>
              <DialogTrigger asChild>
                <Button className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add Bookmark
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Add New Bookmark</DialogTitle>
                </DialogHeader>
                <BookmarkForm isSubmitting={isSubmitting} onSubmit={handleAddBookmark} />
              </DialogContent>
            </Dialog>
          </div>

          <Dialog open={showEditForm} onOpenChange={setShowEditForm}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Edit Bookmark</DialogTitle>
              </DialogHeader>
              <BookmarkForm
                isSubmitting={isSubmitting}
                onSubmit={handleEditBookmark}
                initialData={
                  editingBookmark
                    ? {
                        url: editingBookmark.url,
                        title: editingBookmark.title,
                        notes: editingBookmark.notes,
                      }
                    : undefined
                }
                isEditing={true}
              />
            </DialogContent>
          </Dialog>

          {error && (
            <div className="mb-6 p-4 rounded-lg border border-destructive/20 bg-destructive/10">
              <div className="flex items-center justify-between">
                <p className="text-destructive font-medium">Error: {error}</p>
                <Button variant="outline" size="sm" onClick={refetch}>
                  Retry
                </Button>
              </div>
            </div>
          )}
        </div>

        <BookmarkList
          bookmarks={bookmarks}
          onDelete={handleDeleteBookmark}
          onEdit={handleEditClick} // Added onEdit prop to BookmarkList
        />
      </SignedIn>

      <SignedOut>
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-20 h-20 mb-6 rounded-full bg-muted flex items-center justify-center">
            <svg className="w-10 h-10 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-4">Welcome to Bookmark Manager</h2>
          <p className="text-muted-foreground max-w-md mb-8">
            Sign in to start organizing and managing your favorite links in one beautiful place
          </p>
        </div>
      </SignedOut>
    </div>
  )
}

export default Home
