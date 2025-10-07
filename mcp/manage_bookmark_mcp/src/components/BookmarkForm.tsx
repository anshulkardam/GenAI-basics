"use client"

import type React from "react"

import type { CreateBookmarkData } from "@/types/bookmark"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Loader2 } from "lucide-react"

interface BookmarkFormProps {
  onSubmit: (data: CreateBookmarkData) => void
  initialData?: Partial<CreateBookmarkData>
  isEditing?: boolean
  isSubmitting: boolean
}

export default function BookmarkForm({
  onSubmit,
  initialData,
  isEditing = false,
  isSubmitting = false,
}: BookmarkFormProps) {
  const [formData, setFormData] = useState<CreateBookmarkData>({
    url: initialData?.url || "",
    title: initialData?.title || "",
    notes: initialData?.notes || "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.url.trim() || !formData.title.trim() || isSubmitting) {
      return
    }
    onSubmit(formData)

    if (!isEditing) {
      setFormData({
        url: "",
        title: "",
        notes: "",
      })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="url" className="text-sm font-medium">
          URL <span className="text-destructive">*</span>
        </Label>
        <Input
          type="url"
          id="url"
          value={formData.url}
          onChange={(e) => setFormData((prev) => ({ ...prev, url: e.target.value }))}
          placeholder="https://example.com"
          required
          disabled={isSubmitting}
          className="w-full"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="title" className="text-sm font-medium">
          Title <span className="text-destructive">*</span>
        </Label>
        <Input
          type="text"
          id="title"
          value={formData.title}
          onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
          placeholder="Enter bookmark title"
          required
          disabled={isSubmitting}
          className="w-full"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="notes" className="text-sm font-medium">
          Notes
        </Label>
        <Textarea
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData((prev) => ({ ...prev, notes: e.target.value }))}
          placeholder="Add any notes about this bookmark..."
          disabled={isSubmitting}
          className="w-full min-h-[80px] resize-none"
        />
      </div>

      <div className="flex justify-end pt-4">
        <Button
          disabled={isSubmitting || !formData.url.trim() || !formData.title.trim()}
          type="submit"
          className="min-w-[120px]"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              {isEditing ? "Updating..." : "Saving..."}
            </>
          ) : isEditing ? (
            "Update Bookmark"
          ) : (
            "Save Bookmark"
          )}
        </Button>
      </div>
    </form>
  )
}
