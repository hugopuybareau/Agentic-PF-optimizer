import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export default function Login() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md bg-card shadow-lg rounded-xl p-8">
        <Tabs defaultValue="login" className="w-full">
          <TabsList className="w-full mb-6">
            <TabsTrigger value="login" className="w-1/2">
              Connexion
            </TabsTrigger>
            <TabsTrigger value="register" className="w-1/2">
              Inscription
            </TabsTrigger>
          </TabsList>
          <TabsContent value="login">
            <form className="space-y-4">
              <div>
                <Label htmlFor="login-email">Email</Label>
                <Input
                  id="login-email"
                  type="email"
                  placeholder="Votre email"
                  autoComplete="email"
                />
              </div>
              <div>
                <Label htmlFor="login-password">Mot de passe</Label>
                <Input
                  id="login-password"
                  type="password"
                  placeholder="Votre mot de passe"
                  autoComplete="current-password"
                />
              </div>
              <Button className="w-full mt-2" type="submit">
                Se connecter
              </Button>
            </form>
          </TabsContent>
          <TabsContent value="register">
            <form className="space-y-4">
              <div>
                <Label htmlFor="register-email">Email</Label>
                <Input
                  id="register-email"
                  type="email"
                  placeholder="Votre email"
                  autoComplete="email"
                />
              </div>
              <div>
                <Label htmlFor="register-password">Mot de passe</Label>
                <Input
                  id="register-password"
                  type="password"
                  placeholder="Choisissez un mot de passe"
                  autoComplete="new-password"
                />
              </div>
              <Button className="w-full mt-2" type="submit">
                Créer un compte
              </Button>
            </form>
          </TabsContent>
        </Tabs>
        <div className="my-6 flex items-center gap-4">
          <Separator className="flex-1" />
          <span className="text-xs text-muted-foreground">ou</span>
          <Separator className="flex-1" />
        </div>
        <Button className="w-full" variant="outline" type="button">
          {/* Icône Google possible ici plus tard */}
          Se connecter avec Google
        </Button>
      </div>
    </div>
  );
}
