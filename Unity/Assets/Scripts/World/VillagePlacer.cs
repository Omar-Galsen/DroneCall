using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

// DroneCall / Ashen Realm village placer.
// Put this script anywhere under Assets, attach it to an empty GameObject,
// assign house prefabs from Assets/Art/Environment/Village/Houses, then Build Village.
public class VillagePlacer : MonoBehaviour
{
    [Header("Village house prefabs")]
    public GameObject[] houses;

    [Header("Layout")]
    [Min(1)] public int houseCount = 10;
    public float radius = 28f;
    public float roadHalfWidth = 4f;
    public Vector2 scaleRange = new Vector2(0.9f, 1.1f);
    public int seed = 2026;

    [ContextMenu("Build Village")]
    public void BuildVillage()
    {
        ClearVillage();
        if (houses == null || houses.Length == 0) {
            Debug.LogError("VillagePlacer: assign prefabs from Art/Environment/Village/Houses.");
            return;
        }

        var root = new GameObject("Generated_Village");
        root.transform.SetParent(transform, false);
        var rng = new System.Random(seed);

        for (int i = 0; i < houseCount; i++)
        {
            float t = (i + 0.5f) / houseCount;
            float angle = t * Mathf.PI * 2f + ((float)rng.NextDouble() - .5f) * .28f;
            float r = radius * (.62f + .34f * (float)rng.NextDouble());

            // Leave a broad central road/courtyard instead of filling the middle.
            Vector3 local = new Vector3(Mathf.Cos(angle) * r, 0f, Mathf.Sin(angle) * r);
            if (Mathf.Abs(local.x) < roadHalfWidth) local.x = Mathf.Sign(local.x == 0 ? 1 : local.x) * roadHalfWidth;

            GameObject prefab = houses[rng.Next(houses.Length)];
#if UNITY_EDITOR
            GameObject h = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
#else
            GameObject h = Instantiate(prefab);
#endif
            h.name = "VillageHouse_" + (i + 1).ToString("00");
            h.transform.SetParent(root.transform, false);
            h.transform.localPosition = local;

            // Front roughly faces the village center.
            Vector3 towardCenter = -new Vector3(local.x, 0f, local.z);
            if (towardCenter.sqrMagnitude > .001f)
                h.transform.localRotation = Quaternion.LookRotation(towardCenter.normalized);

            float s = Mathf.Lerp(scaleRange.x, scaleRange.y, (float)rng.NextDouble());
            h.transform.localScale = Vector3.one * s;

            // Place the model on whatever terrain/ground collider is below it.
            Vector3 world = h.transform.position + Vector3.up * 100f;
            if (Physics.Raycast(world, Vector3.down, out RaycastHit hit, 250f))
                h.transform.position = hit.point;
        }
        Debug.Log("VillagePlacer: built " + houseCount + " houses.");
    }

    [ContextMenu("Clear Village")]
    public void ClearVillage()
    {
        Transform old = transform.Find("Generated_Village");
        if (!old) return;
#if UNITY_EDITOR
        if (!Application.isPlaying) DestroyImmediate(old.gameObject);
        else Destroy(old.gameObject);
#else
        Destroy(old.gameObject);
#endif
    }
}

#if UNITY_EDITOR
[CustomEditor(typeof(VillagePlacer))]
public class VillagePlacerEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        var v = (VillagePlacer)target;
        GUILayout.Space(8);
        if (GUILayout.Button("Build Village")) v.BuildVillage();
        if (GUILayout.Button("Clear Village")) v.ClearVillage();
    }
}
#endif
