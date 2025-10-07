import type React from "react";
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";
import "./globals.css";
import { Button } from "@/components/ui/button";
import { BookMarkedIcon } from "lucide-react";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className="dark">
        <head>
          <link
            href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
            rel="stylesheet"
          />
        </head>
        <body className="font-sans antialiased">
          <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container mx-auto flex h-16 items-center justify-between px-6">
              <div className="flex items-center space-x-2">
                <BookMarkedIcon />
                <h1 className="text-xl font-semibold text-foreground">
                  Bookmark Manager
                </h1>
              </div>
              <div className="flex items-center space-x-3">
                <SignedOut>
                  <SignInButton>
                    <Button variant="ghost" size="sm">
                      Sign in
                    </Button>
                  </SignInButton>
                  <SignUpButton>
                    <Button size="sm">Sign up</Button>
                  </SignUpButton>
                </SignedOut>
                <SignedIn>
                  <UserButton />
                </SignedIn>
              </div>
            </div>
          </header>
          <main className="min-h-screen bg-background">{children}</main>
        </body>
      </html>
    </ClerkProvider>
  );
}
