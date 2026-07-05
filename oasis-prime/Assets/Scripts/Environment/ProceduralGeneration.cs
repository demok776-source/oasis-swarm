using UnityEngine;

namespace OasisPrime.Environment
{
    public class ProceduralGeneration : MonoBehaviour
    {
        public int width = 256;
        public int depth = 256;
        public float scale = 20f;
        public float heightMultiplier = 5f;

        void Start()
        {
            Terrain terrain = GetComponent<Terrain>();
            if (terrain != null)
            {
                terrain.terrainData = GenerateTerrain(terrain.terrainData);
            }
        }

        TerrainData GenerateTerrain(TerrainData terrainData)
        {
            terrainData.heightmapResolution = width + 1;
            terrainData.size = new Vector3(width, heightMultiplier, depth);
            terrainData.SetHeights(0, 0, GenerateHeights());
            return terrainData;
        }

        float[,] GenerateHeights()
        {
            float[,] heights = new float[width, depth];
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < depth; y++)
                {
                    heights[x, y] = CalculateHeight(x, y);
                }
            }
            return heights;
        }

        float CalculateHeight(int x, int y)
        {
            float xCoord = (float)x / width * scale;
            float yCoord = (float)y / depth * scale;
            return Mathf.PerlinNoise(xCoord, yCoord);
        }
    }
}
