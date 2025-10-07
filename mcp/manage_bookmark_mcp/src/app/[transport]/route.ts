import { verifyClerkToken } from "@clerk/mcp-tools/next";
import {
  createMcpHandler,
  experimental_withMcpAuth as withMcpAuth,
} from "@vercel/mcp-adapter";
import { auth, clerkClient } from "@clerk/nextjs/server";
import z from "zod";
import { createUserBookmark, getUserBookmarks } from "@/lib/bookmark-utils";
import { CreateBookmarkData } from "@/types/bookmark";

const handler = createMcpHandler((server) => {
  server.tool(
    "get-user-bookmarks",
    "Gets all bookmarks for the authenticated user",
    {},
    async (_, { authInfo }) => {
      try {
        const userId = authInfo!.extra!.userId! as string;
        const bookmarks = await getUserBookmarks(userId);

        return {
          content: [{ type: "text", text: JSON.stringify(bookmarks) }],
        };
      } catch (error) {
        return {
          content: [{ type: "text", text: `error: ${error}` }],
        };
      }
    }
  ),
    server.tool(
      "create-user-bookmark",
      "creates a new bookmark for the authenticated user",
      {
        url: z.string().describe("The URL of the bookmark to create"),
        titles: z.string().describe("The title of the bookmark"),
        notes: z
          .string()
          .describe("Additional Notes for the bookmark")
          .optional(),
      },
      async (args, { authInfo }) => {
        try {
          const userId = authInfo!.extra!.userId! as string;
          const bookmarkData: CreateBookmarkData = {
            url: args.url,
            title: args.titles,
            notes: args.notes || "",
          };

          const newBookmark = await createUserBookmark(userId, bookmarkData);

          return {
            content: [
              {
                type: "text",
                text: ` Created new Bookmark: ${JSON.stringify(newBookmark)}`,
              },
            ],
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: `error: ${error}` }],
          };
        }
      }
    );
});

// The rest of your code...

const authHandler = withMcpAuth(
  handler,
  async (_, token) => {
    const clerkAuth = await auth({ acceptsToken: "oauth_token" });
    return verifyClerkToken(clerkAuth, token);
  },
  {
    required: true,
    resourceMetadataPath: "/.well-known/oauth-protected-resource/mcp",
  }
);

export { authHandler as GET, authHandler as POST };
