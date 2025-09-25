-- XenoLite Script Template
local FreeKey = "{FREE_KEY}"  -- Bot will replace this automatically

-- Services
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local LocalPlayer = Players.LocalPlayer
local Camera = workspace.CurrentCamera

-- GUI Library (Rayfield)
local Rayfield = loadstring(game:HttpGet('https://sirius.menu/rayfield'))()

-- Create main GUI
local Window = Rayfield:CreateWindow({
    Name = "XenoLite",
    LoadingTitle = "Free Key Required",
    LoadingSubtitle = "By Xeno",
})

-- ESP Variables
local ESPEnabled = false
local ESPFolder = Instance.new("Folder", game.CoreGui)
ESPFolder.Name = "XenoLiteESP"

-- Clear ESP
local function ClearESP()
    for _,v in pairs(ESPFolder:GetChildren()) do
        v:Destroy()
    end
end

-- Create ESP for player
local function CreateESP(plr)
    if plr ~= LocalPlayer then
        local box = Drawing.new("Square")
        box.Thickness = 2
        box.Color = Color3.fromRGB(0,255,0)
        box.Filled = false

        local name = Drawing.new("Text")
        name.Size = 14
        name.Color = Color3.fromRGB(255,255,255)
        name.Center = true

        local conn
        conn = RunService.RenderStepped:Connect(function()
            if ESPEnabled and plr.Character and plr.Character:FindFirstChild("HumanoidRootPart") then
                local root = plr.Character.HumanoidRootPart
                local pos, vis = Camera:WorldToViewportPoint(root.Position)
                if vis then
                    local hum = plr.Character:FindFirstChild("Humanoid")
                    local size = 2000 / (pos.Z + 1)
                    box.Size = Vector2.new(size/2, size)
                    box.Position = Vector2.new(pos.X - box.Size.X/2, pos.Y - box.Size.Y/2)
                    box.Visible = true

                    local hp = hum and math.floor(hum.Health) or 0
                    local dist = math.floor((root.Position - LocalPlayer.Character.HumanoidRootPart.Position).Magnitude)

                    name.Text = plr.Name.." | "..hp.." HP | "..dist.."m"
                    name.Position = Vector2.new(pos.X, pos.Y - size/2 - 14)
                    name.Visible = true
                else
                    box.Visible = false
                    name.Visible = false
                end
            else
                box.Visible = false
                name.Visible = false
            end
        end)

        plr.AncestryChanged:Connect(function(_, parent)
            if not parent then
                box:Remove()
                name:Remove()
                conn:Disconnect()
            end
        end)
    end
end

-- ESP Tab
local Tab = Window:CreateTab("ESP")
Tab:CreateToggle({
    Name = "Enable ESP",
    CurrentValue = false,
    Callback = function(value)
        ESPEnabled = value
        ClearESP()
        if value then
            for _,plr in ipairs(Players:GetPlayers()) do
                CreateESP(plr)
            end
            Players.PlayerAdded:Connect(CreateESP)
        end
    end
})

-- Bypass Tab (Visual Only)
local Tab2 = Window:CreateTab("Bypass")
local bypassEnabled = false
Tab2:CreateButton({
    Name = "Toggle Bypass",
    Callback = function()
        bypassEnabled = not bypassEnabled
        if bypassEnabled then
            Rayfield:Notify({Title="Bypass", Content="Bypass enabled 🛡️", Duration=3})
            task.wait(3)
        else
            Rayfield:Notify({Title="Bypass", Content="Turning off bypass...", Duration=1})
            task.wait(2)
            Rayfield:Notify({Title="Bypass", Content="Bypass turned off", Duration=3})
        end
    end
})

print("✅ XenoLite loaded. Free Key:", FreeKey)
