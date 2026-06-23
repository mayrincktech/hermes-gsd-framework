import NextAuth from "next-auth";
import type { NextRequest } from "next/server";
import Credentials from "next-auth/providers/credentials";
import GitHub from "next-auth/providers/github";
import { DrizzleAdapter } from "@auth/drizzle-adapter";
import bcrypt from "bcryptjs";
import { eq } from "drizzle-orm";
import { getDb } from "./db";
import { users } from "./db/schema";

type AuthInstance = ReturnType<typeof NextAuth>;

let _auth: AuthInstance | null = null;

function initAuth(): AuthInstance {
  if (_auth) return _auth;

  const db = getDb();

  _auth = NextAuth({
    adapter: DrizzleAdapter(db),
    session: { strategy: "jwt" },
    providers: [
      Credentials({
        credentials: {
          email: { type: "email" },
          password: { type: "password" },
        },
        authorize: async (credentials) => {
          const email = credentials?.email as string;
          const password = credentials?.password as string;

          if (!email || !password) return null;

          const [user] = await db
            .select()
            .from(users)
            .where(eq(users.email, email));

          if (!user || !user.password) return null;

          const valid = await bcrypt.compare(password, user.password);
          if (!valid) return null;

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            image: user.image,
          };
        },
      }),
      ...(process.env.AUTH_GITHUB_ID && process.env.AUTH_GITHUB_SECRET
        ? [
            GitHub({
              clientId: process.env.AUTH_GITHUB_ID,
              clientSecret: process.env.AUTH_GITHUB_SECRET,
            }),
          ]
        : []),
    ],
    callbacks: {
      async jwt({ token, user }) {
        if (user) {
          token.id = user.id;
        }
        return token;
      },
      async session({ session, token }) {
        if (token && session.user) {
          session.user.id = token.id as string;
        }
        return session;
      },
    },
  });

  return _auth;
}

// Lazy exports — the NextAuth instance is only created on first request,
// not at module evaluation time. This allows `next build` to succeed
// without DATABASE_URL set.
export const handlers = {
  GET: (req: NextRequest) => initAuth().handlers.GET(req),
  POST: (req: NextRequest) => initAuth().handlers.POST(req),
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function auth(...args: any[]) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (initAuth().auth as any)(...args);
}

export function signIn(...args: Parameters<AuthInstance["signIn"]>) {
  return initAuth().signIn(...args);
}

export function signOut(...args: Parameters<AuthInstance["signOut"]>) {
  return initAuth().signOut(...args);
}
