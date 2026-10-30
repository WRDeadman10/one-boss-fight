# Persona Owner Click Steps: `ABP_Greystone_VisualBridge` (A-255)

> **Asset Path**: `/Game/OneBossFight/GreystonePack/ABP_Greystone_VisualBridge`  
> **Target Skeleton**: `/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton`  
> **Retarget Asset**: `/Game/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone`  
> **Engine Target**: Unreal Engine 5.5.4 (Persona Animation Blueprint Editor)  
> **Execution Mode**: Owner GUI Action (~30-60 seconds in Editor)

---

## Step 1: Create the Animation Blueprint Asset

1. In the **Content Drawer / Content Browser**, navigate to the destination folder:
   ```text
   /Game/OneBossFight/GreystonePack/
   ```
2. **Right-Click** in an empty space in the Asset View panel.
3. In the context menu, navigate to:
   $$\text{Animation} \longrightarrow \text{Animation Blueprint}$$
4. In the **Create Animation Blueprint** modal dialog:
   - Under **Target Skeleton**, search for and select:
     ```text
     Greystone_Skeleton
     ```
     *(Path: `/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton`)*
   - Leave Parent Class as default (`AnimInstance`).
   - Click **Create**.
5. Name the newly created asset exactly:
   ```text
   ABP_Greystone_VisualBridge
   ```

---

## Step 2: Open Persona and Navigate to AnimGraph

1. **Double-click** `ABP_Greystone_VisualBridge` to open it in the Persona editor.
2. In the **My Blueprint** panel (top-left dock):
   - Under the **Graphs** section, double-click **`AnimGraph`** to open the animation graph canvas.
3. On the canvas, confirm the default root node is present:
   ```text
   Output Pose  [Result]
   ```

---

## Step 3: Add `Retarget Pose From Mesh` Node

1. **Right-click** in an empty area of the AnimGraph canvas to summon the node context menu.
2. In the search box, type:
   ```text
   Retarget Pose From Mesh
   ```
3. Click on the action:
   $$\text{Retarget Pose From Mesh}$$
   *(Instantiates `AnimNode_RetargetPoseFromMesh` onto the canvas).*

---

## Step 4: Assign the Retarget Asset Property

1. Click on the newly placed **`Retarget Pose From Mesh`** node to select it.
2. In the **Details** panel (docked on the right side of the screen):
   - Locate the category: **Retarget**
   - Locate the property: **`Retarget Asset`**
   - Click the asset picker dropdown and select:
     ```text
     RTG_CombatMannequin_To_Greystone
     ```
     *(Path: `/Game/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone`)*

---

## Step 5: Wire the Graph Pins

1. On the **`Retarget Pose From Mesh`** node:
   - Click and drag from the output pin labeled **`Pose`** (white running-man icon on the right edge).
2. Drag the connection wire into the **`Result`** input pin on the **`Output Pose`** node.
3. Release the mouse button. The wire should turn solid white, connecting:
   $$\text{[Retarget Pose From Mesh (Pose)]} \longrightarrow \text{[Output Pose (Result)]}$$

---

## Step 6: Compile and Save

1. In the top-left toolbar, click the **Compile** button (keyboard shortcut: `F7`).
   - Confirm a **Green Checkmark** appears over the Compile icon.
2. In the toolbar, click **Save** (disk icon, keyboard shortcut: `Ctrl+S`).
3. Close the Persona editor window.

---

## Step 7: Asset Acceptance Verification Checklist

- [ ] File exists on disk: `Content/OneBossFight/GreystonePack/ABP_Greystone_VisualBridge.uasset`
- [ ] Asset references `Greystone_Skeleton`
- [ ] AnimGraph contains exactly two nodes: `Retarget Pose From Mesh` wired directly into `Output Pose`
- [ ] `Retarget Asset` property is explicitly set to `RTG_CombatMannequin_To_Greystone`
- [ ] Asset compiles cleanly with zero compilation warnings or errors
