"use client";

import * as React from "react";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { toIsoDate } from "@/lib/format";
import { cn } from "@/lib/utils";

interface DatePickerProps {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  invalid?: boolean;
  className?: string;
}

export function DatePicker({ id, value, onChange, invalid, className }: DatePickerProps) {
  const [open, setOpen] = React.useState(false);
  const date = value ? new Date(`${value}T00:00:00`) : undefined;
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        render={
          <Button
            id={id}
            variant="outline"
            aria-invalid={invalid || undefined}
            className={cn(
              "w-full justify-between bg-background font-normal",
              !date && "text-muted-foreground",
              className,
            )}
          />
        }
      >
        {date ? format(date, "MMM d, yyyy") : <span>Pick a date</span>}
        <CalendarIcon className="size-4 text-muted-foreground" />
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={date}
          defaultMonth={date}
          captionLayout="dropdown"
          startMonth={today}
          endMonth={new Date(today.getFullYear() + 5, 11)}
          onSelect={(selected) => {
            if (!selected) return; // ignore deselecting the current day
            onChange(toIsoDate(selected));
            setOpen(false);
          }}
          disabled={{ before: today }}
          autoFocus
        />
      </PopoverContent>
    </Popover>
  );
}
