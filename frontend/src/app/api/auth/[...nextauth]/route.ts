import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "TU_CLIENT_ID",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "TU_CLIENT_SECRET",
    }),
  ],
  pages: {
    signIn: "/auth/signin", // Ruta personalizada si queremos, aunque usaremos el default por ahora
  },
  callbacks: {
    async session({ session, token }) {
      if (session.user) {
        // Enviar el token al frontend para que pueda mandarlo al backend
        (session as any).accessToken = token.accessToken;
      }
      return session;
    },
  }
});

export { handler as GET, handler as POST };
