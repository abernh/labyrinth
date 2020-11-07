import { mount } from "@vue/test-utils";
import VMazeCard from "@/components/VMazeCard.vue";
import MazeCard from "@/model/mazeCard.js";
import Player from "@/model/player.js";

const wrapperFactory = (
    props = {
        mazeCard: new MazeCard(0, 0, 0, "NSEW", 0)
    }
) => {
    return mount(VMazeCard, {
        propsData: { ...props }
    });
};

describe("VMazeCard", () => {
    it("contains an svg-element", () => {
        const wrapper = wrapperFactory();
        expect(wrapper.contains("svg")).toBe(true);
    });

    it("has width of 100 if cardSize is 100", () => {
        const wrapper = wrapperFactory();
        expect(wrapper.element.getAttribute("width")).toBe("100");
    });

    it("includes north outPath if MazeCard has a north outPath", () => {
        const wrapper = wrapperFactory({
            mazeCard: new MazeCard(0, 0, 0, "NW", 0)
        });
        expect(wrapper.find({ ref: "north" }).exists()).toBeTruthy();
    });

    it("does not include north outPath if MazeCard object does not have a north outPath", () => {
        const wrapper = wrapperFactory({
            mazeCard: new MazeCard(0, 0, 0, "EW", 0)
        });
        expect(wrapper.find({ ref: "north" }).exists()).toBeFalsy();
    });

    it("does not render players if the MazeCard object does not contain pieces", () => {
        const wrapper = wrapperFactory({
            mazeCard: new MazeCard(0, 0, 0, "EW", 0)
        });
        expect(wrapper.findAll("player-piece").length).toBe(0);
    });

    it("renders a single player", () => {
        var mazeCard = new MazeCard(0, 0, 0, "EW", 0);
        mazeCard.addPlayer(Player.withId(0));
        const wrapper = wrapperFactory({
            mazeCard: mazeCard
        });
        expect(wrapper.findAll(".player-piece").length).toBe(1);
    });

    it("renders two players without overlap", () => {
        var mazeCard = new MazeCard(0, 0, 0, "EW", 0);
        mazeCard.addPlayer(Player.withId(0));
        mazeCard.addPlayer(Player.withId(1));
        const wrapper = wrapperFactory({
            mazeCard: mazeCard
        });
        var playerPieces = wrapper.findAll(".player-piece__shape");
        expect(playerPieces.length).toBe(2);
        var cx0 = Number.parseFloat(playerPieces.at(0).element.getAttribute("cx"));
        var cy0 = Number.parseFloat(playerPieces.at(0).element.getAttribute("cy"));
        var cx1 = Number.parseFloat(playerPieces.at(1).element.getAttribute("cx"));
        var cy1 = Number.parseFloat(playerPieces.at(1).element.getAttribute("cy"));
        var r0 = Number.parseFloat(playerPieces.at(0).element.getAttribute("r"));
        var r1 = Number.parseFloat(playerPieces.at(1).element.getAttribute("r"));
        var distance = Math.sqrt(Math.pow(cx0 - cx1, 2) + Math.pow(cy0 - cy1, 2));
        var radiusSums = r0 + r1;
        expect(distance).toBeGreaterThan(radiusSums);
    });

    it("renders an objective if MazeCard has one", () => {
        let mazeCard = new MazeCard(0, 0, 0, "EW", 0);
        mazeCard.hasObject = true;
        const wrapper = wrapperFactory({
            mazeCard: mazeCard
        });
        expect(wrapper.findAll(".objective").length).toBe(1);
    });

    it("does not render an objective if MazeCard has none", () => {
        let mazeCard = new MazeCard(0, 0, 0, "EW", 0);
        mazeCard.hasObject = false;
        const wrapper = wrapperFactory({
            mazeCard: mazeCard
        });
        expect(wrapper.findAll(".objective").length).toBe(0);
    });
});
