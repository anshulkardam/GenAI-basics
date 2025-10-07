import { deleteUserBookmark, UpdateUserBookmark } from "@/lib/bookmark-utils";
import { auth } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;

    await deleteUserBookmark(userId, id);

    return NextResponse.json("Bookmark deleted successfully", { status: 200 });
  } catch (error) {
    console.error("Error deleting bookmark: ", error);
    return NextResponse.json(
      { error: "Failed to delete bookmark" },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;

    const body = await request.json();
    const { url, title, notes } = body;

    if (!url || !title) {
      return NextResponse.json(
        { error: "URL and Title are required" },
        { status: 400 }
      );
    }

    const updatedBookmark = await UpdateUserBookmark(userId, id, {
      url,
      title,
      notes,
    });

    return NextResponse.json(updatedBookmark, { status: 200 });
  } catch (error) {
    console.error("Error updating bookmark: ", error);
    return NextResponse.json(
      { error: "Failed to update bookmark" },
      { status: 500 }
    );
  }
}
