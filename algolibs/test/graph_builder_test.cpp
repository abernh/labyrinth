#include "graphbuilder/text_graph_builder.h"
#include "graphbuilder/snake_graph_builder.h"

#include "util.h"

#include "gtest/gtest.h"
#include <set>

using namespace labyrinth;

class GraphBuilderFromTextTest : public ::testing::Test {
protected:

    void SetUp() override {
        TextGraphBuilder builder{};
        const std::vector<std::string> maze{
            "###|#.#|#.#|",
            "#..|...|..#|",
            "#.#|#.#|###|",
            "------------",
            "#.#|###|###|",
            "#..|...|...|",
            "#.#|###|###|",
            "------------",
            "#.#|#.#|###|",
            "#..|#.#|..#|",
            "###|#.#|#.#|",
            "------------"
        };
        builder.setMaze(maze);
        graph_ = builder.buildGraph();
    }

    MazeGraph graph_{0};
};

TEST_F(GraphBuilderFromTextTest, getNumberOfNodes_returnsCorrectValue) {
    EXPECT_EQ(graph_.getNumberOfNodes(), 9);
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow0Column0_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 0}, {Location{0, 1}, Location{1, 0}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow0Column1_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 1}, {Location{0, 0}, Location{0, 2}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow0Column2_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 2}, {Location{0, 1}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow1Column0_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 0}, {Location{0, 0}, Location{1, 1}, Location{2, 0}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow1Column1_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 1}, {Location{1, 0}, Location{1, 2}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow1Column2_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 2}, {Location{1, 1}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow2Column0_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{2, 0}, {Location{1, 0}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow2Column1_returnsNoNeighbors) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location{2, 1}, 0));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow2Column2_returnsNoNeighbors) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location{2, 2}, 0));
}

TEST(GraphBuilderSnakeTest, OneNodeForExtentOfOne) {
    SnakeGraphBuilder builder{};
    builder.setExtent(1);
    MazeGraph graph = builder.buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 1);
}

TEST(GraphBuilderSnakeTest, CorrectNeighborsForExtentOfTwo) {
    SnakeGraphBuilder builder{};
    builder.setExtent(2);
    MazeGraph graph = builder.buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 4);
    EXPECT_TRUE(hasNeighbors(graph, Location{0, 0}, {Location{0, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{0, 1}, {Location{0, 0}, Location{1, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{1, 0}, {Location{1, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{1, 1}, {Location{0, 1}, Location{1, 0}}));
}

TEST(GraphBuilderSnakeTest, CorrectNeighborsForExtentOfThree) {
    SnakeGraphBuilder builder{};
    builder.setExtent(3);
    MazeGraph graph = builder.buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 9);
    EXPECT_TRUE(hasNeighbors(graph, Location{0, 0}, {Location{0, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{0, 1}, {Location{0, 0}, Location{0, 2}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{0, 2}, {Location{0, 1}, Location{1, 2}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{1, 2}, {Location{0, 2}, Location{1, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{1, 1}, {Location{1, 2}, Location{1, 0}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{1, 0}, {Location{1, 1}, Location{2, 0}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{2, 0}, {Location{1, 0}, Location{2, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{2, 1}, {Location{2, 0}, Location{2, 2}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{2, 2}, {Location{2, 1}}));
}

TEST(GraphBuilderSnakeTest, OpenEndedPathForExtentOfThirty) {
    SnakeGraphBuilder builder{};
    size_t extent = 30;
    builder.setExtent(extent);
    MazeGraph graph = builder.buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 900);
    for (auto row = 0u; row < extent; row++) {
        for (auto column = 0u; column < extent; column++) {
            if (row == 0 && column == 0) {
                EXPECT_TRUE(assertNumNeighbors(graph, Location{row, column}, 1))
                    << "Top left corner does not have exactly one neighbor";
            }
            else if (row == extent - 1 && column == 0) {
                EXPECT_TRUE(assertNumNeighbors(graph, Location{row, column}, 1))
                    << "Bottom left corner does not have exactly one neighbor";
            }
            else {
                EXPECT_TRUE(assertNumNeighbors(graph, Location{row, column}, 2))
                    << "Node at position " << Location{row, column} << " does not have exactly two neighbors";
            }
        }
    }
}

TEST(GraphBuilderSnakeTest, OpenEndedPathForExtentOfThirtyOne) {
    SnakeGraphBuilder builder{};
    size_t extent = 31;
    builder.setExtent(extent);
    MazeGraph graph = builder.buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 961);
    for (auto row = 0u; row < extent; row++) {
        for (auto column = 0u; column < extent; column++) {
            if (row == 0 && column == 0) {
                EXPECT_TRUE(assertNumNeighbors(graph, Location{row, column}, 1))
                    << "Top left corner does not have exactly one neighbor";
            }
            else if (row == extent - 1 && column == extent - 1) {
                EXPECT_TRUE(assertNumNeighbors(graph, Location{row, column}, 1))
                    << "Bottom right corner does not have exactly one neighbor";
            }
            else {
                EXPECT_TRUE(assertNumNeighbors(graph, Location{row, column}, 2))
                    << "Node at position " << Location{row, column} << " does not have exactly two neighbors";
            }
        }
    }
}
