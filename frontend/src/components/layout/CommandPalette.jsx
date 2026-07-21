import { useNavigate } from 'react-router-dom';
import {
  CommandDialog, CommandEmpty, CommandGroup, CommandInput,
  CommandItem, CommandList, CommandSeparator, CommandShortcut,
} from '@/components/ui/command';
import { NAV_ITEMS } from '@/config/navigation';
import { useCommandPalette } from '@/contexts/CommandPaletteContext';
import { APP_SHELL } from '@/constants/testIds';
import { Sparkles, Search, Settings, User } from 'lucide-react';

export function CommandPalette() {
  const { open, setOpen } = useCommandPalette();
  const navigate = useNavigate();

  const go = (path) => {
    setOpen(false);
    navigate(path);
  };

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <div data-testid={APP_SHELL.commandPalette}>
        <CommandInput
          placeholder="Type a command or search…"
          data-testid={APP_SHELL.commandPaletteInput}
        />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>

          <CommandGroup heading="Navigate">
            {NAV_ITEMS.map((n) => {
              const Icon = n.icon;
              return (
                <CommandItem
                  key={n.key}
                  onSelect={() => go(n.path)}
                  data-testid={`cmdk-nav-${n.key}`}
                >
                  <Icon className="h-4 w-4 mr-2 text-muted-foreground" />
                  {n.label}
                </CommandItem>
              );
            })}
          </CommandGroup>

          <CommandSeparator />

          <CommandGroup heading="Quick actions">
            <CommandItem onSelect={() => go('/app/ai-mentor')}>
              <Sparkles className="h-4 w-4 mr-2 text-primary" /> Ask AI Mentor
              <CommandShortcut>⌘M</CommandShortcut>
            </CommandItem>
            <CommandItem onSelect={() => go('/app/settings')}>
              <Settings className="h-4 w-4 mr-2" /> Open Settings
              <CommandShortcut>⌘,</CommandShortcut>
            </CommandItem>
            <CommandItem onSelect={() => go('/app/profile')}>
              <User className="h-4 w-4 mr-2" /> View Profile
            </CommandItem>
            <CommandItem onSelect={() => go('/app/mission-control')}>
              <Search className="h-4 w-4 mr-2" /> Mission Control
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </div>
    </CommandDialog>
  );
}
